# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: calculator.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'calculator.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x63\x61lculator.proto\x12\ncalculator\"F\n\x12\x43\x61lculationRequest\x12\x0c\n\x04num1\x18\x01 \x01(\x02\x12\x0c\n\x04num2\x18\x02 \x01(\x02\x12\x14\n\x0coperation_id\x18\x03 \x01(\t\"c\n\x13\x43\x61lculationResponse\x12\x0e\n\x06result\x18\x01 \x01(\x02\x12\x14\n\x0coperation_id\x18\x02 \x01(\t\x12\x0f\n\x07success\x18\x03 \x01(\x08\x12\x15\n\rerror_message\x18\x04 \x01(\t2\xc1\x02\n\nCalculator\x12H\n\x03\x41\x64\x64\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponse\"\x00\x12M\n\x08Subtract\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponse\"\x00\x12M\n\x08Multiply\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponse\"\x00\x12K\n\x06\x44ivide\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'calculator_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CALCULATIONREQUEST']._serialized_start=32
  _globals['_CALCULATIONREQUEST']._serialized_end=102
  _globals['_CALCULATIONRESPONSE']._serialized_start=104
  _globals['_CALCULATIONRESPONSE']._serialized_end=203
  _globals['_CALCULATOR']._serialized_start=206
  _globals['_CALCULATOR']._serialized_end=527
# @@protoc_insertion_point(module_scope)
