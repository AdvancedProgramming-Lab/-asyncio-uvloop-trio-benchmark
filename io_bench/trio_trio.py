import trio
import time
import os

# Diretório onde os arquivos de teste estão localizados
DIR = "test_files"

# Função assíncrona para ler o conteúdo de um arquivo
async def read_file(path):
    # trio.open_file é o equivalente nativo do trio para I/O de arquivos
    async with await trio.open_file(path, "r") as f:
        await f.read()

# Função assíncrona para escrever dados em um arquivo
async def write_file(path, data):
    async with await trio.open_file(path, "w") as f:
        await f.write(data)

async def main():
    start = time.perf_counter()
    
    paths = [os.path.join(DIR, f) for f in os.listdir(DIR)]
    
    # --- Lote 1: Leitura ---
    # Em Trio, usamos "nurseries" (berçários) para concorrência estruturada.
    # O bloco "async with" só termina quando todas as tarefas dentro dele acabarem.
    async with trio.open_nursery() as nursery:
        for p in paths:
            # start_soon agenda a tarefa para execução imediata
            nursery.start_soon(read_file, p)
            
    # --- Lote 2: Escrita ---
    # Abrimos um novo nursery para garantir que a escrita só ocorra (ou seja agrupada)
    # separadamente da leitura, mantendo a lógica do script original.
    async with trio.open_nursery() as nursery:
        for p in paths:
            nursery.start_soon(write_file, p + "_out", "Test data")

    end = time.perf_counter()
    print(f"trio: file I/O in {end - start:.9f} seconds")
    return end - start

if __name__ == "__main__":
    # Garante que o diretório existe para evitar erros na primeira execução
    if not os.path.exists(DIR):
        print(f"Error: Directory '{DIR}' not found. Please create it and add files.")
        exit(1)

    res = []

    for _ in range(20):
        # trio.run recebe a função diretamente, não a corrotina (main())
        res.append(trio.run(main))

    # --- Cálculos Estatísticos ---
    mean = sum(res) / len(res)
    stddev = (sum((x - mean)**2 for x in res) / len(res))**0.5

    print("--- Stats (Trio) ---")
    print(f"mean: {mean:.9f} seconds")
    print(f"min: {min(res):.9f} seconds")
    print(f"max: {max(res):.9f} seconds")
    print(f"stddev: {stddev:.9f} seconds")
    print(f"total: {sum(res):.9f} seconds")

    # --- Limpeza (Cleanup) ---
    for f in os.listdir(DIR):
        if f.endswith("_out"): # Verificação de segurança adicional
             out_file = os.path.join(DIR, f)
             os.remove(out_file)
