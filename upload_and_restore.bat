@echo off
echo Miesposa0526 > temp_pass.txt
pscp -pw Miesposa0526 "d:\ESCRITORIO\OpticaApp\backup_final.json" root@84.247.129.180:/var/www/opticaapp/
pscp -pw Miesposa0526 "d:\ESCRITORIO\OpticaApp\restore_backup.sh" root@84.247.129.180:/var/www/opticaapp/
del temp_pass.txt
plink -pw Miesposa0526 root@84.247.129.180 "chmod +x /var/www/opticaapp/restore_backup.sh && /var/www/opticaapp/restore_backup.sh"
