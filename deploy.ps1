# Start pymilvus in a new window
Start-Process -FilePath "milvus-server" 

# Start django rfp_api in a new window
Start-Process -FilePath "python" -ArgumentList "manage.py runserver 0.0.0.0:8000"
