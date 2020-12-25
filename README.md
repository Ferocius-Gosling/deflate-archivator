## Deflate archiver
Архиватор, использующий алгоритм Deflate, основанный на идее LZ77+Huffman

#### Установка:
```bash
git clone https://github.com/Ferocius-Gosling/deflate-archivator.git
# установка зависимостей
pip install -r requirements.txt 
```

#### Для запуска:
```
python -m deflate <compress/decompress> <filename/archivename> <archivename>
```
#### Compress
Произойдёт архивация файла с именем filename в архив archivename
#### Decompress
Произойдёт распаковка архива с именем archivename

### Пример использования
```bash
python -m deflate compress example.txt archive_example
``` 
