python run_picking.py
copy picking.csv ..\blackberry\

cd ..\blackberry\
python run_washer.py
copy classifying.csv ..\strawberry\

cd ..\strawberry\
python run_bulk.py
python classification.py

cd ..\blueberry\
