FROM python:3.7.9

ARG UID=999

ENV APP_LOC=/gof2bountybot
ENV SAVE_LOC=/saveData
ENV SHIPS_LOC=/ships

COPY . $APP_LOC
RUN pip install --requirement $APP_LOC/requirements.txt

RUN useradd --system --shell /bin/false --uid $UID bountybot
RUN mkdir $SAVE_LOC $SHIPS_LOC
RUN chown -R bountybot:bountybot $SAVE_LOC $SHIPS_LOC $APP_LOC

USER bountybot
RUN ln -s $SAVE_LOC $APP_LOC/saveData
RUN ln -s $SHIPS_LOC $APP_LOC/ships

WORKDIR $APP_LOC
VOLUME $SAVE_LOC
VOLUME $SHIPS_LOC
ENTRYPOINT ["/usr/bin/python3", "./main.py"]
