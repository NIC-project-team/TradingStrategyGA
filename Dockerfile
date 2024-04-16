FROM python:3.11.5

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
RUN tar xvzf ta-lib-0.4.0-src.tar.gz
WORKDIR ta-lib
RUN ./configure --prefix=/usr && make && make install
WORKDIR /

RUN pip install ta-lib
RUN pip install freqtrade
RUN pip install scikit-optimize

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD space_optimizer.py /space_optimizer.py

ADD strategy_generator.py /strategy_generator.py

ADD user_data /user_data

ENTRYPOINT ["python", "/space_optimizer.py"]