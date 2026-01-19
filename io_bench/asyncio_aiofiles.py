import aiofiles
import asyncio
import time
import os

# Diretório onde os arquivos de teste estão localizados
DIR = "test_files"

# Função assíncrona para ler o conteúdo de um arquivo
async def read_file(path):
    # Abre o arquivo em modo leitura ("r") de forma não bloqueante
    async with aiofiles.open(path, "r") as f:
        await f.read() # Lê o conteúdo (neste caso, apenas para teste de performance)

# Função assíncrona para escrever dados em um arquivo
async def write_file(path, data):
    # Abre o arquivo em modo escrita ("w") de forma não bloqueante
    async with aiofiles.open(path, "w") as f:
        await f.write(data)

async def main():
    start = time.perf_counter() # Inicia o cronômetro de alta precisão
    
    # Lista todos os caminhos completos dos arquivos no diretório
    paths = [os.path.join(DIR, f) for f in os.listdir(DIR)]
    
    # Executa todas as tarefas de LEITURA simultaneamente
    # O gather agrupa as corrotinas e aguarda que todas terminem
    await asyncio.gather(*(read_file(p) for p in paths))

    # Executa todas as tarefas de ESCRITA simultaneamente
    # Cria um novo arquivo com o sufixo "_out" para cada arquivo original
    await asyncio.gather(*(write_file(p + "_out", "Test data") for p in paths))
    
    end = time.perf_counter() # Para o cronômetro
    print(f"asyncio: file I/O in {end - start:.9f} seconds")
    return end - start

if __name__ == "__main__":
    res = []
    # Executa o loop de teste 10 vezes para obter uma média estatística
    for _ in range(20):
        # asyncio.run() gerencia o loop de eventos para cada execução
        res.append(asyncio.run(main()))

    # --- Cálculos Estatísticos ---
    mean = sum(res) / len(res)
    # Cálculo do desvio padrão para medir a consistência da performance
    stddev = (sum((x - mean)**2 for x in res) / len(res))**0.5

    print("--- Stats (Asyncio) ---")
    print(f"mean: {mean:.9f} seconds")
    print(f"min: {min(res):.9f} seconds")
    print(f"max: {max(res):.9f} seconds")
    print(f"stddev: {stddev:.9f} seconds")
    print(f"total: {sum(res):.9f} seconds")

    # --- Limpeza (Cleanup) ---
    # Remove os arquivos temporários "_out" criados durante o teste
    for f in os.listdir(DIR):
        out_file = os.path.join(DIR, f + "_out")
        if os.path.exists(out_file):
            os.remove(out_file)
