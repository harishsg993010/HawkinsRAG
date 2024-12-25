+------------------+     +------------------+     +------------------+
|   Data Sources   |     |   HawkinsRAG    |     |    HawkinsDB    |
|  (Files, APIs,   | --> |   (Processing,   | --> |   (Storage &    |
|   Databases)     |     |    Loading)      |     |   Retrieval)    |
+------------------+     +------------------+     +------------------+
         |                       |                        |
         v                       v                        v
+------------------+     +------------------+     +------------------+
|    Loaders       |     |    Chunking &    |     |     Query      |
| (Format-specific |     |    Embedding     |     |   Processing   |
|   processing)    |     |                  |     |                |
+------------------+     +------------------+     +------------------+