# Configuración de conexión
$DB_NAME = "password:main"
$DB_USER = "g10usr"
$DB_HOST = "us-east-1.sql.xata.sh"
$DB_PORT = "5432"
$DB_PASSWORD = "xau_Gaspu1Ulo7rZSnNDlPpQUs6V5MxaFL4Z1"  # Reemplaza esto con tu API Key real

# Activar SSL
$env:PGPASSWORD = $DB_PASSWORD
$env:PGSSLMODE = "require"

# Crear carpeta de respaldo si no existe
$backupFolder = "C:\Respaldos"
if (-not (Test-Path $backupFolder)) {
    New-Item -ItemType Directory -Path $backupFolder | Out-Null
}

# Nombre del archivo con fecha y hora
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$backupFolder\xata_backup_$timestamp.sql"

# Ejecutar pg_dump desde PostgreSQL 18
& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" `
  -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME `
  --no-owner --no-privileges --format=p --file=$BACKUP_FILE

# Confirmación
if (Test-Path $BACKUP_FILE) {
    Write-Output "✅ Respaldo completado: $BACKUP_FILE"
} else {
    Write-Output "❌ Error: No se generó el archivo de respaldo."
}
