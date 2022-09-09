@ECHO OFF

SET /a step=0
SET rule=loose

ECHO Start from step-%step% (%rule% mode)


IF %step% LEQ 0 GOTO CLEAN
IF %step% LEQ 1 GOTO STEP-1
IF %step% LEQ 2 GOTO STEP-2
IF %step% LEQ 3 GOTO STEP-3
IF %step% LEQ 4 GOTO STEP-4


::============CLEAN============
:CLEAN
CD ..\blueberry\
DEL /Q *.csv
CD ..\blackberry\
DEL /Q *.csv
CD ..\strawberry\
DEL /Q *.csv
RMDIR /S/Q saved_model
RMDIR /S/Q test
RMDIR /S/Q train
GOTO END


::============STEP-1============
:STEP-1
:: 筛选
ECHO Picking...
CD ..\blueberry\
:: 移除目标文件
DEL /Q picking.csv
python run_picking.py
COPY picking.csv ..\blackberry\


::============STEP-2============
:STEP-2
:: 按规则分类
ECHO Washer...
IF "%rule%" == "loose" GOTO LOOSE
IF "%rule%" == "strict" GOTO STRICT
:STEP-2-END
GOTO STEP-3

:LOOSE
ECHO using loose mode
CD ..\blackberry\
DEL /Q classifying.csv
python run_washer.py
COPY classifying.csv ..\strawberry\
GOTO STEP-2-END

:STRICT
ECHO using strict mode
CD ..\blueberry\
:: 移除目标文件
DEL /Q classifying.csv
python run_classifying.py
COPY classifying.csv ..\strawberry\
GOTO STEP-2-END


::============STEP-3============
:STEP-3
:: 绘图
ECHO Bulk
CD ..\strawberry\
:: 移除目标文件
RMDIR /S/Q test
RMDIR /S/Q train
python run_bulk.py

::============STEP-4============
:STEP-4
:: 学习分类
ECHO Classification
CD ..\strawberry\
:: 移除目标文件
RMDIR /S/Q saved_model
python classification.py

::============END============
:END
:: 返回
CD ..\blueberry\
