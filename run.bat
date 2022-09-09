@ECHO OFF

SET /a step=0
SET rule=losse

ECHO Start from step-%step% (%rule% mode)


IF %step% LEQ 0 GOTO CLEAN
IF %step% LEQ 1 GOTO STEP-1
IF %step% LEQ 2 GOTO STEP-2
IF %step% LEQ 3 GOTO STEP-3
IF %step% LEQ 4 GOTO STEP-4


::============CLEAN============
:CLEAN
CD ..\blueberry\
DEL *.csv
CD ..\blackberry\
DEL *.csv
CD ..\strawberry\
DEL *.csv
RMDIR /S/Q saved_model
RMDIR /S/Q test
RMDIR /S/Q train
GOTO END


::============STEP-1============
:STEP-1
:: 筛选
ECHO Picking...
CD ..\blueberry\
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
python run_washer.py
COPY classifying.csv ..\strawberry\
GOTO STEP-2-END

:STRICT
ECHO using strict mode
CD ..\blueberry\
python run_classifying.py
COPY classifying.csv ..\strawberry\
GOTO STEP-2-END


::============STEP-3============
:STEP-3
:: 绘图
ECHO Bulk
CD ..\strawberry\
python run_bulk.py

::============STEP-4============
:STEP-4
:: 学习分类
ECHO Classification
CD ..\strawberry\
python classification.py

::============END============
:END
:: 返回
CD ..\blueberry\
