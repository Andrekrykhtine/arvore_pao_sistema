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

// ========================
// FUNCIONALIDADES DE IA
// ========================

class AIFeatures {
    constructor() {
        this.aiEndpoints = {
            insights: '/api/v1/ai/insights',
            restockSuggestions: '/api/v1/ai/restock-suggestions',
            trainModels: '/api/v1/ai/train-models'
        };
    }

    async loadAIInsights() {
        try {
            const response = await fetch(this.aiEndpoints.insights);
            if (!response.ok) {
                // Se modelos não estão treinados, treinar primeiro
                if (response.status === 400) {
                    await this.trainModels();
                    return await this.loadAIInsights();
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const insights = await response.json();
            this.displayAIInsights(insights);
            return insights;
            
        } catch (error) {
            console.error('Erro ao carregar insights IA:', error);
            this.showAIError('Erro ao carregar insights de IA');
        }
    }

    async trainModels() {
        try {
            console.log('🤖 Treinando modelos de IA...');
            const response = await fetch(this.aiEndpoints.trainModels, { method: 'POST' });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ Modelos treinados:', result);
            
            this.showAISuccess(`Modelos IA treinados! ${result.models_trained} modelos com ${result.training_samples} amostras`);
            
        } catch (error) {
            console.error('Erro ao treinar modelos:', error);
            this.showAIError('Erro ao treinar modelos de IA');
        }
    }

    displayAIInsights(insights) {
        // Criar seção de IA no dashboard se não existir
        let aiSection = document.getElementById('ai-insights-section');
        if (!aiSection) {
            aiSection = document.createElement('div');
            aiSection.id = 'ai-insights-section';
            aiSection.className = 'row mt-4';
            
            const dashboardContent = document.querySelector('.container-fluid .row:last-child');
            dashboardContent.parentNode.insertBefore(aiSection, dashboardContent.nextSibling);
        }

        aiSection.innerHTML = `
            <div class="col-12">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-robot me-2"></i>Insights de IA - Sistema Árvore Pão</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h3 class="text-primary">${insights.produtos_precisam_reposicao}</h3>
                                    <p class="mb-0">Produtos Precisam Reposição</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h3 class="text-success">R$ ${insights.economia_estimada_otimizacao.toLocaleString('pt-BR')}</h3>
                                    <p class="mb-0">Economia Estimada</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h3 class="text-info">${insights.demanda_total_prevista_7d.toFixed(1)}</h3>
                                    <p class="mb-0">Demanda Prevista 7d</p>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h3 class="text-warning">${insights.score_saude_ia}%</h3>
                                    <p class="mb-0">Score Saúde IA</p>
                                </div>
                            </div>
                        </div>
                        
                        <hr>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-chart-line me-2"></i>Tendências Identificadas:</h6>
                                <ul class="list-unstyled">
                                    ${insights.tendencias_identificadas.map(t => `<li><i class="fas fa-arrow-right text-primary me-2"></i>${t}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-lightbulb me-2"></i>Recomendações Estratégicas:</h6>
                                <ul class="list-unstyled">
                                    ${insights.recomendacoes_estrategicas.map(r => `<li><i class="fas fa-check text-success me-2"></i>${r}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6><i class="fas fa-star me-2"></i>Produtos Alta Prioridade:</h6>
                                <div class="d-flex flex-wrap gap-2">
                                    ${insights.produtos_alta_prioridade.map(p => `<span class="badge bg-warning text-dark">${p}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-12 text-center">
                                <button class="btn btn-primary btn-sm me-2" onclick="aiFeatures.loadRestockSuggestions()">
                                    <i class="fas fa-boxes me-1"></i>Ver Sugestões Reposição
                                </button>
                                <button class="btn btn-success btn-sm me-2" onclick="aiFeatures.trainModels()">
                                    <i class="fas fa-robot me-1"></i>Retreinar IA
                                </button>
                                <small class="text-muted">Gerado em: ${new Date(insights.gerado_em).toLocaleString('pt-BR')}</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadRestockSuggestions() {
        try {
            const response = await fetch(this.aiEndpoints.restockSuggestions);
            const suggestions = await response.json();
            
            this.displayRestockSuggestions(suggestions);
            
        } catch (error) {
            console.error('Erro ao carregar sugestões:', error);
            this.showAIError('Erro ao carregar sugestões de reposição');
        }
    }

    displayRestockSuggestions(suggestions) {
        // Criar modal para mostrar sugestões
        const modalHtml = `
            <div class="modal fade" id="restockModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"><i class="fas fa-robot me-2"></i>Sugestões de Reposição IA</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Produto</th>
                                            <th>Categoria</th>
                                            <th>Estoque</th>
                                            <th>Sugestão</th>
                                            <th>Urgência</th>
                                            <th>Custo</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${suggestions.map(s => `
                                            <tr>
                                                <td><strong>${s.produto_nome}</strong><br><small class="text-muted">${s.motivo_ia}</small></td>
                                                <td><span class="badge bg-secondary">${s.categoria}</span></td>
                                                <td>${s.estoque_atual}<br><small class="text-muted">${s.dias_para_acabar} dias</small></td>
                                                <td class="text-primary"><strong>${s.quantidade_sugerida}</strong></td>
                                                <td><span class="badge ${this.getUrgencyClass(s.urgencia)}">${s.urgencia}</span></td>
                                                <td>R$ ${s.custo_estimado.toLocaleString('pt-BR')}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                            <button type="button" class="btn btn-primary">Gerar Pedido Automático</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remover modal existente se houver
        const existingModal = document.getElementById('restockModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Adicionar novo modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('restockModal'));
        modal.show();
    }

    getUrgencyClass(urgencia) {
        const classes = {
            'CRITICA': 'bg-danger',
            'ALTA': 'bg-warning', 
            'MEDIA': 'bg-info',
            'BAIXA': 'bg-success'
        };
        return classes[urgencia] || 'bg-secondary';
    }

    showAISuccess(message) {
        const alertHtml = `
            <div class="alert alert-success alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 1050;" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', alertHtml);
    }

    showAIError(message) {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 1050;" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', alertHtml);
    }
}

// Instanciar funcionalidades de IA
const aiFeatures = new AIFeatures();

// Modificar o dashboard principal para incluir IA
const originalDashboard = ArvorepaoDashboard.prototype.loadDashboardData;
ArvorepaoDashboard.prototype.loadDashboardData = async function() {
    // Carregar dados originais
    await originalDashboard.call(this);
    
    // Carregar insights de IA
    await aiFeatures.loadAIInsights();
};
