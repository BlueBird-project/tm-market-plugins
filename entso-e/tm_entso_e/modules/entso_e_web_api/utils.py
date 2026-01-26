import xml.etree.ElementTree as ET
from typing import Dict, Tuple, get_origin, get_args, Union

from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo


class XMLBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    # TODO:
    # wrapped list  <users><user/><user/></users> (not supported) vs non wrapped <user/><user/> (supported)
    @classmethod
    def get_aliased_fields(cls) -> Dict[str, Tuple[str, FieldInfo]]:
        aliases = {}
        for mk, mf in cls.model_fields.items():
            if mf.alias is None:
                # todo: log warning
                aliases[mk] = (mk, mf)
            else:
                aliases[mf.alias] = (mk, mf)
        return aliases

    @staticmethod
    def process_field(fi: FieldInfo, current_ele: ET.Element, namespace_len: int, skip_fields: bool):
        field_annotation = fi.annotation
        f_origin = get_origin(field_annotation)
        # handle union
        if f_origin is not None and f_origin is Union:
            f_args = get_args(field_annotation)
            f_args = [f_arg for f_arg in f_args if f_arg is not type(None)]
            assert len(f_args) == 1
            field_annotation = f_args[0]
            f_origin = get_origin(field_annotation)
        if f_origin is not None:
            f_args = get_args(field_annotation)
            if f_origin is list:
                # todo write some text error
                assert len(f_args) == 1
                if issubclass(f_args[0], XMLBaseModel):
                    processed_obj = f_args[0].from_xml(current_ele, namespace_len, skip_fields)
                    # expected list
                    return [processed_obj]
                else:
                    # expected list
                    return [f_args[0](current_ele.text.strip())]
            elif f_origin is Union:
                raise Exception("TODO: nested union")
            else:
                raise Exception("Not supported case :TODO: ")
        else:
            if issubclass(field_annotation, XMLBaseModel):
                processed_obj = field_annotation.from_xml(current_ele, namespace_len, skip_fields)
                return processed_obj
            else:
                return field_annotation(current_ele.text.strip())

    @classmethod
    def from_xml(cls, root_ele: ET.Element, namespace_len: int, skip_fields=False):
        aliased_fields = cls.get_aliased_fields()
        obj_dict = {}
        for ele in root_ele:
            # TODO: catch key error
            try:
                tag_name = ele.tag[namespace_len:]
                field_name, field_info = aliased_fields[tag_name]
                processed_value = XMLBaseModel.process_field(fi=field_info, current_ele=ele,
                                                             namespace_len=namespace_len, skip_fields=skip_fields)
                if field_name in obj_dict:
                    # its list
                    obj_dict[field_name].append(processed_value[0])
                else:
                    obj_dict[field_name] = processed_value
            except KeyError as ex:
                if skip_fields:
                    # todo:log warning
                    pass
                else:
                    # TODO: make error more details
                    raise ex
        return cls(**obj_dict)
