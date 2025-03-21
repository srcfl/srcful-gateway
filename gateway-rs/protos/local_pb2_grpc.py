# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import protos.local_pb2 as local__pb2


class apiStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.pubkey = channel.unary_unary(
                '/helium.local.api/pubkey',
                request_serializer=local__pb2.pubkey_req.SerializeToString,
                response_deserializer=local__pb2.pubkey_res.FromString,
                )
        self.region = channel.unary_unary(
                '/helium.local.api/region',
                request_serializer=local__pb2.region_req.SerializeToString,
                response_deserializer=local__pb2.region_res.FromString,
                )
        self.router = channel.unary_unary(
                '/helium.local.api/router',
                request_serializer=local__pb2.router_req.SerializeToString,
                response_deserializer=local__pb2.router_res.FromString,
                )
        self.add_gateway = channel.unary_unary(
                '/helium.local.api/add_gateway',
                request_serializer=local__pb2.add_gateway_req.SerializeToString,
                response_deserializer=local__pb2.add_gateway_res.FromString,
                )


class apiServicer(object):
    """Missing associated documentation comment in .proto file."""

    def pubkey(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def region(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def router(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def add_gateway(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_apiServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'pubkey': grpc.unary_unary_rpc_method_handler(
                    servicer.pubkey,
                    request_deserializer=local__pb2.pubkey_req.FromString,
                    response_serializer=local__pb2.pubkey_res.SerializeToString,
            ),
            'region': grpc.unary_unary_rpc_method_handler(
                    servicer.region,
                    request_deserializer=local__pb2.region_req.FromString,
                    response_serializer=local__pb2.region_res.SerializeToString,
            ),
            'router': grpc.unary_unary_rpc_method_handler(
                    servicer.router,
                    request_deserializer=local__pb2.router_req.FromString,
                    response_serializer=local__pb2.router_res.SerializeToString,
            ),
            'add_gateway': grpc.unary_unary_rpc_method_handler(
                    servicer.add_gateway,
                    request_deserializer=local__pb2.add_gateway_req.FromString,
                    response_serializer=local__pb2.add_gateway_res.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'helium.local.api', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class api(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def pubkey(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/helium.local.api/pubkey',
            local__pb2.pubkey_req.SerializeToString,
            local__pb2.pubkey_res.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def region(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/helium.local.api/region',
            local__pb2.region_req.SerializeToString,
            local__pb2.region_res.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def router(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/helium.local.api/router',
            local__pb2.router_req.SerializeToString,
            local__pb2.router_res.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def add_gateway(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/helium.local.api/add_gateway',
            local__pb2.add_gateway_req.SerializeToString,
            local__pb2.add_gateway_res.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
