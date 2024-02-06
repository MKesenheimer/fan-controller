# builder image
FROM ubuntu:latest AS builder

RUN apt-get update && apt-get install --no-install-recommends -y python3 python3-dev python3-venv python3-pip python3-wheel build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN python3 -m venv /home/user/fan-controller/venv
ENV PATH="/home/user/fan-controller/venv/bin:$PATH"

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt


# runner image
FROM ubuntu:latest AS runner
LABEL Description="fan-controller"

RUN apt-get update && apt-get install --no-install-recommends -y python3 python3-venv && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

#RUN mkdir -p /share/froling-data
RUN useradd --create-home user
RUN mkdir /home/user/fan-controller
COPY --from=builder /home/user/fan-controller/venv /home/user/fan-controller/venv
WORKDIR /home/user/fan-controller
COPY . .
RUN chown -R user:user /home/user/fan-controller
#RUN chown -R user:user /share/froling-data
RUN chmod a+x /home/user/fan-controller/run.sh

# change user
#USER user

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

# activate virtual environment
ENV VIRTUAL_ENV=/home/user/fan-controller/venv
ENV PATH="/home/user/fan-controller/venv/bin:$PATH"

#CMD ["/bin/bash"]
CMD ["./run.sh"]
