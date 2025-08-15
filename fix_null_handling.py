import psycopg2
from psycopg2.extras import RealDictCursor

def get_produtos_safe():
    """Buscar produtos com tratamento seguro de valores NULL"""
    try:
        conn = psycopg2.connect(
            dbname="arvore_pao",
            user="postgres", 
            password="123456",
            host="db",
            port=5432
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query com COALESCE para tratar NULLs na origem
            cursor.execute("""
                SELECT 
                    id,
                    nome,
                    categoria,
                    COALESCE(preco_venda, 0.0) as preco_venda,
                    COALESCE(preco_custo, 0.0) as preco_custo,
                    COALESCE(quantidade_atual, 0.0) as quantidade_atual,
                    COALESCE(quantidade_minima, 0.0) as quantidade_minima,
                    is_active
                FROM produtos 
                WHERE is_active = true
                ORDER BY id
            """)
            
            produtos = cursor.fetchall()
            
            # Converter para dicionários Python seguros
            produtos_safe = []
            for produto in produtos:
                produto_dict = dict(produto)
                
                # Garantir que nenhum valor seja None
                produto_dict['preco_venda'] = max(0.1, float(produto_dict.get('preco_venda', 0) or 0))
                produto_dict['preco_custo'] = max(0.1, float(produto_dict.get('preco_custo', 0) or 0))
                produto_dict['quantidade_atual'] = max(0.0, float(produto_dict.get('quantidade_atual', 0) or 0))
                produto_dict['quantidade_minima'] = max(0.0, float(produto_dict.get('quantidade_minima', 0) or 0))
                
                produtos_safe.append(produto_dict)
                
            print(f"✅ Produtos carregados com segurança: {len(produtos_safe)}")
            for p in produtos_safe[:2]:  # Debug primeiros 2
                print(f"   {p['nome']}: qty={p['quantidade_atual']}, preco={p['preco_venda']}")
                
            return produtos_safe
            
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Testar função
if __name__ == "__main__":
    produtos = get_produtos_safe()
    print(f"Total: {len(produtos)} produtos")
