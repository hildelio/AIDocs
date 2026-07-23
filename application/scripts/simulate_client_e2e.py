import sys
import json
import time
import requests
import boto3
from datetime import datetime

# Usage: python simulate_client_e2e.py <api_gateway_url>

def main():
    if len(sys.argv) < 2:
        print("Usage: python simulate_client_e2e.py <api_gateway_url>")
        sys.exit(1)

    api_url = sys.argv[1]
    
    # Environment config
    USER_ID = "user-e2e-test"
    FILENAME = "sample_invoice.txt"
    TABLE_NAME = "startup-xyz-dev-data" # Baseado no nome provisionado pelo terraform no dev env
    
    # Mock: Criar arquivo local
    file_content = b"NOTA FISCAL - Valor R$ 500,00\nFornecedor: Teste E2E"
    with open(FILENAME, "wb") as f:
        f.write(file_content)
    print(f"[*] Arquivo '{FILENAME}' criado localmente.")

    # Passo 1: API Gateway (Ingestão)
    print(f"[*] Iniciando Ingestão - Requisitando presigned URL para '{api_url}'...")
    start_time = time.time()
    
    try:
        response = requests.post(
            api_url,
            json={"user_id": USER_ID, "filename": FILENAME},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] Erro ao contatar a API: {e}")
        sys.exit(1)
        
    document_id = data.get("document_id")
    upload_url = data.get("upload_url")
    
    if not document_id or not upload_url:
        print(f"[!] Resposta da API inválida: {data}")
        sys.exit(1)
        
    print(f"[*] Document ID gerado: {document_id}")
    print(f"[*] Upload URL obtida com sucesso.")

    # Passo 2: Upload S3
    print(f"[*] Realizando upload do arquivo via PUT S3...")
    try:
        put_response = requests.put(upload_url, data=file_content)
        put_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Falha no upload para o S3: {e}")
        sys.exit(1)
        
    print(f"[*] Upload concluído. Latência Ingestão+Upload: {time.time() - start_time:.2f} segundos.")

    # Passo 3: Polling DynamoDB
    print(f"[*] Iniciando Polling no DynamoDB aguardando processamento do Textract (Timeout: 60s)...")
    dynamodb = boto3.resource('dynamodb', region_name='sa-east-1')
    table = dynamodb.Table(TABLE_NAME)
    
    max_attempts = 20
    sleep_time = 3
    final_item = None
    
    polling_start = time.time()
    
    for attempt in range(1, max_attempts + 1):
        try:
            db_response = table.get_item(Key={'id': document_id})
            item = db_response.get('Item')
            
            if item:
                status = item.get('status')
                print(f"  -> Tentativa {attempt}/{max_attempts} | Status: {status}")
                
                if status in ["PROCESSED", "FAILED", "FAILED_EXTERNAL_DEPENDENCY"]:
                    final_item = item
                    break
            else:
                print(f"  -> Tentativa {attempt}/{max_attempts} | Item não encontrado ainda...")
                
        except Exception as e:
            print(f"[!] Erro ao consultar o DynamoDB: {e}")
            break
            
        time.sleep(sleep_time)

    # Passo 4: Output Limpo
    total_time = time.time() - start_time
    print("\n" + "="*50)
    print("RESULTADO FINAL E2E")
    print("="*50)
    
    if not final_item:
        print("[!] Timeout atingido (60s) ou erro antes da conclusão.")
        print(f"Document ID: {document_id}")
    else:
        status = final_item.get('status')
        extracted_text = final_item.get('extracted_text', '')
        
        print(f"Document ID: {document_id}")
        print(f"Status Final: {status}")
        print(f"Tempo Total E2E: {total_time:.2f} segundos")
        print(f"Tempo de Polling OCR: {time.time() - polling_start:.2f} segundos")
        
        if status == "PROCESSED":
            print(f"Caracteres Extraídos: {len(extracted_text)}")
            print("-" * 50)
            print("Trecho do Texto (Max 300 chars):")
            print(extracted_text[:300] + ("..." if len(extracted_text) > 300 else ""))
        else:
            print("[!] Falha no processamento (Verificar CloudWatch Logs).")
            
    print("="*50)

if __name__ == "__main__":
    main()
