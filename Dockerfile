FROM python:3.7.9-slim-buster

# Arguments and environment
ARG UID=999
ENV APP_LOC=/gof2bountybot
ENV SAVE_LOC=/saveData
ENV SHIPS_LOC=/ships

# Create user and copy source in
RUN useradd --system --shell /bin/false --uid $UID bountybot
COPY --chown=bountybot . $APP_LOC

# Prep system with dependencies
RUN pip install --requirement $APP_LOC/requirements.txt
RUN apt-get install --no-install-recommends -y blender

# Create directory structure and links
RUN mkdir $SAVE_LOC $SHIPS_LOC
RUN chown -R bountybot:bountybot $SAVE_LOC $SHIPS_LOC
USER bountybot
RUN ln -s $SAVE_LOC $APP_LOC/saveData
RUN ln -s $SHIPS_LOC $APP_LOC/ships

# Volumes, workdir and entrypoint
WORKDIR $APP_LOC
VOLUME $SAVE_LOC
VOLUME $SHIPS_LOC
ENTRYPOINT ["/usr/bin/python3", "./main.py"]
