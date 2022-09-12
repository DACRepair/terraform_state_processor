FROM python:3-alpine as build
WORKDIR /build

ENV SETUP_VERSION development

COPY terraform_state_processor ./terraform_state_processor
COPY setup.py .

RUN python3 ./setup.py build \
    && python3 ./setup.py bdist_wheel


FROM python:3-alpine as run

WORKDIR /tmp/wheel
COPY --from=build /build/dist/*.whl .
COPY --from=build /build/dist/*.egg .

RUN for file in *.whl; do pip install $file; done

WORKDIR /data

ENTRYPOINT ["/usr/local/bin/tfstate_processor"]
CMD ["--help"]
