FROM python:3.9-alpine
WORKDIR /root
COPY . .
RUN mkdir -p /root/.config/gpterminator
RUN ls
RUN pip install . 
ARG APIKEY
ENV OPENAI_API_KEY=$APIKEY
CMD ["gpterm"]