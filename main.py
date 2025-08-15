
def get_produtos_para_ia():
    """Função específica para buscar produtos para IA com tratamento robusto de NULL"""
    try:
        conn = psycopg2.connect(
            dbname="arvore_pao",
            user="postgres", 
            password="123456",
            host="db",
            port=5432
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query com COALESCE e validações
            cursor.execute("""
                SELECT 
                    id,
                    COALESCE(nome, 'Produto') as nome,
                    COALESCE(categoria, 'outros') as categoria,
                    COALESCE(NULLIF(preco_venda, 0), 1.0) as preco_venda,
                    COALESCE(NULLIF(preco_custo, 0), 0.6) as preco_custo,
                    COALESCE(quantidade_atual, 10.0) as quantidade_atual,
                    COALESCE(quantidade_minima, 5.0) as quantidade_minima,
                    is_active
                FROM produtos 
                WHERE is_active = true 
                AND (preco_venda IS NOT NULL OR preco_venda > 0)
                ORDER BY id
            """)
            
            produtos = cursor.fetchall()
            
            # Validação final em Python
            produtos_validados = []
            for produto in produtos:
                p = dict(produto)
                
                # Garantir valores numéricos válidos
                p['preco_venda'] = max(0.1, float(p['preco_venda'] or 1.0))
                p['preco_custo'] = max(0.1, float(p['preco_custo'] or p['preco_venda'] * 0.6))
                p['quantidade_atual'] = max(0.0, float(p['quantidade_atual'] or 10.0))
                p['quantidade_minima'] = max(0.0, float(p['quantidade_minima'] or 5.0))
                
                # Validação final - garantir que nada é None
                if all(v is not None for v in [p['preco_venda'], p['preco_custo'], p['quantidade_atual']]):
                    produtos_validados.append(p)
                    
            return produtos_validados
            
    except Exception as e:
        logger.error(f"Erro ao buscar produtos para IA: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()
@app.post("/api/v1/ai/train-models-safe")
def train_ai_models_safe():
    """🤖 Treinamento SEGURO com tratamento robusto de NULL"""
    try:
        logger.info("=== INICIANDO TREINAMENTO SEGURO ===")
        
        # Buscar produtos com tratamento seguro de NULL
        produtos_data = get_produtos_para_ia()
        
        if not produtos_data:
            return {
                "success": False, 
                "error": "Nenhum produto válido encontrado",
                "debug": "Verifique se existem produtos ativos com preços válidos"
            }
            
        logger.info(f"Produtos carregados para IA: {len(produtos_data)}")
        
        # Debug dos primeiros produtos
        for i, produto in enumerate(produtos_data[:3]):
            logger.info(f"Produto {i+1}: {produto['nome']} - "
                       f"Qty: {produto['quantidade_atual']} - "
                       f"Preço: {produto['preco_venda']} - "
                       f"Custo: {produto['preco_custo']}")
        
        # Verificar se forecaster existe
        global forecaster
        if 'forecaster' not in globals():
            from ai_models.demand_forecasting import ArvorepaoDemandForecaster
            forecaster = ArvorepaoDemandForecaster()
        
        # Treinar modelos
        result = forecaster.train_models(produtos_data)
        
        if result.get("success"):
            logger.info("=== TREINAMENTO CONCLUÍDO COM SUCESSO ===")
            return {
                "success": True,
                "models_trained": result["models_trained"],
                "training_samples": result["training_samples"], 
                "feature_count": result["feature_count"],
                "model_metrics": result["model_metrics"],
                "produtos_processados": len(produtos_data),
                "debug_info": {
                    "primeiro_produto": produtos_data[0] if produtos_data else None,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erro desconhecido no treinamento"),
                "produtos_tentativa": len(produtos_data)
            }
            
    except Exception as e:
        error_msg = f"Erro crítico no treinamento seguro: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "error_type": type(e).__name__
        }

def get_produtos_para_ia():
    """Função específica para buscar produtos para IA com tratamento robusto de NULL"""
    try:
        conn = psycopg2.connect(
            dbname="arvore_pao",
            user="postgres", 
            password="123456",
            host="db",
            port=5432
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query com COALESCE e validações
            cursor.execute("""
                SELECT 
                    id,
                    COALESCE(nome, 'Produto') as nome,
                    COALESCE(categoria, 'outros') as categoria,
                    COALESCE(NULLIF(preco_venda, 0), 1.0) as preco_venda,
                    COALESCE(NULLIF(preco_custo, 0), 0.6) as preco_custo,
                    COALESCE(quantidade_atual, 10.0) as quantidade_atual,
                    COALESCE(quantidade_minima, 5.0) as quantidade_minima,
                    is_active
                FROM produtos 
                WHERE is_active = true 
                AND (preco_venda IS NOT NULL OR preco_venda > 0)
                ORDER BY id
            """)
            
            produtos = cursor.fetchall()
            
            # Validação final em Python
            produtos_validados = []
            for produto in produtos:
                p = dict(produto)
                
                # Garantir valores numéricos válidos
                p['preco_venda'] = max(0.1, float(p['preco_venda'] or 1.0))
                p['preco_custo'] = max(0.1, float(p['preco_custo'] or p['preco_venda'] * 0.6))
                p['quantidade_atual'] = max(0.0, float(p['quantidade_atual'] or 10.0))
                p['quantidade_minima'] = max(0.0, float(p['quantidade_minima'] or 5.0))
                
                # Validação final - garantir que nada é None
                if all(v is not None for v in [p['preco_venda'], p['preco_custo'], p['quantidade_atual']]):
                    produtos_validados.append(p)
                    
            return produtos_validados
            
    except Exception as e:
        logger.error(f"Erro ao buscar produtos para IA: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()
@app.post("/api/v1/ai/train-models-safe")
def train_ai_models_safe():
    """🤖 Treinamento SEGURO com tratamento robusto de NULL"""
    try:
        logger.info("=== INICIANDO TREINAMENTO SEGURO ===")
        
        # Buscar produtos com tratamento seguro de NULL
        produtos_data = get_produtos_para_ia()
        
        if not produtos_data:
            return {
                "success": False, 
                "error": "Nenhum produto válido encontrado",
                "debug": "Verifique se existem produtos ativos com preços válidos"
            }
            
        logger.info(f"Produtos carregados para IA: {len(produtos_data)}")
        
        # Debug dos primeiros produtos
        for i, produto in enumerate(produtos_data[:3]):
            logger.info(f"Produto {i+1}: {produto['nome']} - "
                       f"Qty: {produto['quantidade_atual']} - "
                       f"Preço: {produto['preco_venda']} - "
                       f"Custo: {produto['preco_custo']}")
        
        # Verificar se forecaster existe
        global forecaster
        if 'forecaster' not in globals():
            from ai_models.demand_forecasting import ArvorepaoDemandForecaster
            forecaster = ArvorepaoDemandForecaster()
        
        # Treinar modelos
        result = forecaster.train_models(produtos_data)
        
        if result.get("success"):
            logger.info("=== TREINAMENTO CONCLUÍDO COM SUCESSO ===")
            return {
                "success": True,
                "models_trained": result["models_trained"],
                "training_samples": result["training_samples"], 
                "feature_count": result["feature_count"],
                "model_metrics": result["model_metrics"],
                "produtos_processados": len(produtos_data),
                "debug_info": {
                    "primeiro_produto": produtos_data[0] if produtos_data else None,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Erro desconhecido no treinamento"),
                "produtos_tentativa": len(produtos_data)
            }
            
    except Exception as e:
        error_msg = f"Erro crítico no treinamento seguro: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "error_type": type(e).__name__
        }
