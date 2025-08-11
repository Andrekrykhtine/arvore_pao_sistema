class ArvorepaoDashboard {
    constructor() {
        this.apiBase = '/api/v1/analytics';
        this.charts = {};
        this.updateInterval = 30000; // 30 segundos
        this.init();
    }

    async init() {
        console.log('🍞 Iniciando Dashboard Sistema Árvore Pão');
        await this.loadDashboardData();
        this.startAutoUpdate();
    }

    async loadDashboardData() {
        try {
            // Mostrar loading
            this.showLoading();
            
            // Carregar dados em paralelo
            const [resumo, produtos, categorias, alertas] = await Promise.all([
                this.fetchData('/resumo'),
                this.fetchData('/produtos'),
                this.fetchData('/categorias'),
                this.fetchData('/alertas')
            ]);

            // Atualizar KPIs
            this.updateKPIs(resumo);
            
            // Atualizar gráficos
            this.updateCharts(categorias, produtos);
            
            // Atualizar tabela de produtos
            this.updateProdutosTable(produtos);
            
            // Atualizar alertas
            this.updateAlertas(alertas);
            
            // Atualizar timestamp
            this.updateTimestamp();
            
            console.log('✅ Dashboard atualizado com sucesso');
            
        } catch (error) {
            console.error('❌ Erro ao carregar dashboard:', error);
            this.showError('Erro ao carregar dados. Tentando novamente...');
        }
    }

    async fetchData(endpoint) {
        const response = await fetch(`${this.apiBase}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    updateKPIs(resumo) {
        document.getElementById('total-produtos').textContent = resumo.total_produtos || 0;
        document.getElementById('valor-estoque').textContent = 
            `R$ ${parseFloat(resumo.valor_total_estoque || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}`;
        document.getElementById('margem-media').textContent = 
            `${(resumo.margem_media || 0).toFixed(1)}%`;
        
        // Calcular total de alertas (será atualizado quando alertas carregarem)
        document.getElementById('total-alertas').textContent = '-';
    }

    updateCharts(categorias, produtos) {
        // Gráfico de Pizza - Produtos por Categoria
        const ctxCategorias = document.getElementById('chart-categorias').getContext('2d');
        
        if (this.charts.categorias) {
            this.charts.categorias.destroy();
        }
        
        this.charts.categorias = new Chart(ctxCategorias, {
            type: 'pie',
            data: {
                labels: categorias.map(c => c.categoria.toUpperCase()),
                datasets: [{
                    data: categorias.map(c => c.total_produtos),
                    backgroundColor: [
                        '#8B4513', '#D2691E', '#228B22', '#FF8C00', '#DC143C', '#4169E1'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Gráfico de Barras - Top Produtos por Valor
        const ctxProdutos = document.getElementById('chart-top-produtos').getContext('2d');
        
        if (this.charts.produtos) {
            this.charts.produtos.destroy();
        }

        // Top 5 produtos por valor de estoque
        const topProdutos = produtos
            .sort((a, b) => parseFloat(b.valor_estoque_total) - parseFloat(a.valor_estoque_total))
            .slice(0, 5);

        this.charts.produtos = new Chart(ctxProdutos, {
            type: 'bar',
            data: {
                labels: topProdutos.map(p => p.nome),
                datasets: [{
                    label: 'Valor em Estoque (R$)',
                    data: topProdutos.map(p => parseFloat(p.valor_estoque_total)),
                    backgroundColor: '#8B4513',
                    borderColor: '#D2691E',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    updateProdutosTable(produtos) {
        const tbody = document.querySelector('#tabela-produtos tbody');
        tbody.innerHTML = '';

        produtos.slice(0, 10).forEach(produto => {
            const statusClass = this.getStatusClass(produto.status_estoque);
            const statusText = this.getStatusText(produto.status_estoque);
            
            const row = `
                <tr>
                    <td><strong>${produto.nome}</strong></td>
                    <td><span class="badge bg-secondary">${produto.categoria.toUpperCase()}</span></td>
                    <td>${parseFloat(produto.quantidade_atual).toLocaleString('pt-BR')}</td>
                    <td>R$ ${parseFloat(produto.preco_venda).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td>R$ ${parseFloat(produto.valor_estoque_total).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td><span class="badge ${statusClass}">${statusText}</span></td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }

    updateAlertas(alertas) {
        const container = document.getElementById('alertas-container');
        container.innerHTML = '';

        // Atualizar contador de alertas
        document.getElementById('total-alertas').textContent = alertas.length;

        if (alertas.length === 0) {
            container.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>Nenhum alerta ativo!</div>';
            return;
        }

        alertas.slice(0, 5).forEach(alerta => {
            const alertClass = this.getAlertClass(alerta.tipo);
            const iconClass = this.getAlertIcon(alerta.tipo);
            
            const alertHtml = `
                <div class="alert ${alertClass} p-3 mb-2">
                    <div class="d-flex align-items-center">
                        <i class="${iconClass} me-2"></i>
                        <div>
                            <strong>${alerta.titulo}</strong><br>
                            <small>${alerta.descricao}</small>
                        </div>
                        <span class="badge bg-dark ms-auto">${alerta.urgencia}</span>
                    </div>
                </div>
            `;
            container.innerHTML += alertHtml;
        });
    }

    getStatusClass(status) {
        const classes = {
            'normal': 'bg-success',
            'baixo': 'bg-warning', 
            'sem_estoque': 'bg-danger',
            'critico': 'bg-danger'
        };
        return classes[status] || 'bg-secondary';
    }

    getStatusText(status) {
        const texts = {
            'normal': 'Normal',
            'baixo': 'Baixo',
            'sem_estoque': 'Sem Estoque',
            'critico': 'Crítico'
        };
        return texts[status] || 'N/A';
    }

    getAlertClass(tipo) {
        const classes = {
            'CRITICO': 'alert-critico',
            'ALTO': 'alert-alto',
            'MEDIO': 'alert-medio'
        };
        return classes[tipo] || 'alert-info';
    }

    getAlertIcon(tipo) {
        const icons = {
            'CRITICO': 'fas fa-exclamation-triangle text-danger',
            'ALTO': 'fas fa-exclamation-circle text-warning',
            'MEDIO': 'fas fa-info-circle text-info'
        };
        return icons[tipo] || 'fas fa-bell';
    }

    updateTimestamp() {
        const now = new Date();
        document.getElementById('timestamp').textContent = 
            now.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
    }

    showLoading() {
        document.getElementById('total-produtos').innerHTML = '<div class="loading"></div>';
        document.getElementById('valor-estoque').innerHTML = '<div class="loading"></div>';
        document.getElementById('margem-media').innerHTML = '<div class="loading"></div>';
        document.getElementById('total-alertas').innerHTML = '<div class="loading"></div>';
    }

    showError(message) {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.body.insertAdjacentHTML('afterbegin', alertHtml);
    }

    startAutoUpdate() {
        setInterval(() => {
            console.log('🔄 Atualizando dashboard automaticamente...');
            this.loadDashboardData();
        }, this.updateInterval);
    }
}

// Inicializar dashboard quando página carregar
document.addEventListener('DOMContentLoaded', () => {
    new ArvorepaoDashboard();
});
