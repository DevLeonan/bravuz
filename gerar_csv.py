import os
import csv

CAMINHO_CATALOGO = r"C:\Users\Leonan\OneDrive\Área de Trabalho\bravus\catalogo_fornecedor"
NOME_ARQUIVO_FINAL = "planilha_bravus.csv"

def gerar_planilha():
    print(f"🔥 Radar de Gênero e Imagens ativado em: {CAMINHO_CATALOGO}...\n")
    
    if not os.path.exists(CAMINHO_CATALOGO):
        print(f"❌ ERRO: A pasta '{CAMINHO_CATALOGO}' não foi encontrada.")
        return

    with open(NOME_ARQUIVO_FINAL, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        # NOVO: A 5ª coluna agora é o Gênero!
        writer.writerow(['Nome', 'Preco', 'Categoria', 'Caminho_Imagem', 'Genero']) 
        
        total_pecas = 0
        
        for root, dirs, files in os.walk(CAMINHO_CATALOGO):
            # Identificador de Gênero baseado no nome da pasta
            pasta_root_upper = root.upper()
            if "MASCULINO" in pasta_root_upper:
                genero = "M"
            elif "FEMININO" in pasta_root_upper:
                genero = "F"
            else:
                genero = "U" # Unissex se não identificar
                
            for nome_arquivo in files:
                if not nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    continue
                
                pasta_atual = os.path.basename(root)
                categoria_limpa = pasta_atual.strip().title() 
                
                nome_sem_extensao, _ = os.path.splitext(nome_arquivo)
                nome_peca = nome_sem_extensao.strip()
                preco_peca = "0.00"
                
                if '-' in nome_sem_extensao:
                    partes = nome_sem_extensao.split('-')
                    possivel_preco = partes[-1].strip().replace(',', '.')
                    
                    if len(possivel_preco) <= 8:
                        try:
                            float(possivel_preco.replace('R$', '').strip())
                            preco_peca = possivel_preco.replace('R$', '').strip()
                            nome_peca = '-'.join(partes[:-1]).strip() 
                        except ValueError:
                            pass
                
                caminho_imagem_completo = os.path.join(root, nome_arquivo)
                    
                writer.writerow([nome_peca, preco_peca, categoria_limpa, caminho_imagem_completo, genero])
                print(f"✔️ {nome_peca[:20]}... | R$ {preco_peca} | Gênero: {genero}")
                total_pecas += 1
                    
    print(f"\n⚡ SUCESSO! Planilha gerada com {total_pecas} peças classificadas.")

if __name__ == "__main__":
    gerar_planilha()