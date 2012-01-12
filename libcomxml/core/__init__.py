# -*- coding: utf-8 -*-

"""
Core classes for libComXML
==========================

This package contains the very basic classes needed for working with the
models that need to be mapped to XML.

"""

# etree import chain
try:
    from lxml import etree
except ImportError:
    try:
        super(Cabecera, self).__init__(name, root)
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree


class Field(object):
    """Base Field class
    """
    def __init__(self, name, value=None, attributes=None):
        """Constructor

        :param name: the name of the field
        super(Cabecera, self).__init__(name, root)
        :param value: the value of the field
        :param attributes: a dict with optional field attributes
        """
        self.name = name
        self.value = value
        self.attributes = attributes or {}

    def __str__(self):
        return "<Field:%s>" % (self.name,)

    def __unicode__(self):
        return self.__str__()


class XmlField(Field):
    """Field with XML capabilities
    """
    def __init__(self, name, value=None, parent=None, attributes=None):
        """Constructor

        .. see: Field.__init__

        :param attribute: the name of the parent field, for the XML repr.
        """
        self.parent = parent
        super(XmlField, self).__init__(name, value=value, attributes=attributes)

    def _parse_list(self, element, value):
        for val in value:
            if isinstance(val, XmlField):
                val.parent = element.tag
                self.parse_value(element, val)
            elif isinstance(val, XmlModel):
                val.build_tree()
                element.append(val.doc_root)

    def _parse_value(self, element, value=None):
        """Generates the XML for the value according to its type
        """
        if not value:
            value = self.value
        if value:
            if isinstance(value, str):
                element.text = value
            elif isinstance(value, XmlField):
                element.append(value.element())
            elif isinstance(value, XmlModel):
                value.build_tree()
                element.append(value.doc_root)
            elif isinstance(value, list):
                self._parse_list(element, value)
            else:  # default: cast to string
                element.text = str(value)

        return element

    def element(self, parent=None):
        """Constructs the lxml.Element that represents the field

        :param parent: an etree Element to be used as parent for this one
        """
        if parent is not None:
            ele = etree.SubElement(parent, self.name, **self.attributes)
        else:
            ele = etree.Element(self.name, **self.attributes)
        ele = self._parse_value(ele)
        return ele


    def __str__(self):
        """Returns the XML repr of the field

        It does not take care of the parent field, if any.
        """
        return etree.tostring(self.element())

    def __unicode__(self):
        return self.__str__()


class Model(object):
    """Base Model class
    """

    __fields = None
    _sort_order = None


    def __init__(self, name):
        self.name = name


    def sorted_fields(self):
        """Returns a sorted list of the model fields' names.
        """
        if self._sort_order:
            return self._sort_order
        return self._fields.keys()


    def _get_fields(self):
        """Lookups the fields of the model and store them in a dict using the
        field name as key.
        """
        #if self.__fields:
        #    return self.__fields
        fields = {}
        for member in dir(self):
            if not member.startswith('_'): 
                s_member = getattr(self, member)
                if (isinstance(s_member, Field) or
                    isinstance(s_member, Model) or
                    isinstance(s_member, list)):
                    fields[member] = s_member
        self.__fields = fields
        return fields

    _fields = property(fget=_get_fields)


    def feed(self, vals):
        """Populates the vals dictionary to the value property of the fields.

        :param vals: a dictionary with key:value pairs for this model's fields.
        """

        for key in vals:
            if hasattr(self, key):
                field = getattr(self, key)
                if isinstance(field, Field):
                    setattr(field, 'value', vals[key])
                elif isinstance(field, Model) and isinstance(vals[key], Model):
                    setattr(self, key, vals[key])
                else:
                    setattr(self, key, vals[key])


    def __str__(self):
        return "<Model:%s>" % (self.name,)

    def __unicode__(self):
        return self.__str__()

class XmlModel(Model):
    """Model with XML capabilities

    This class is intended to be subclassed and used as follows:

    """

    def __init__(self, name, root):
        self.name = name
        super(XmlModel, self).__init__(name)
        self.root = getattr(self, root)
        self.doc_root = self.root.element()
        self.built = False


    def build_tree(self):
        """Bulids the tree with all the fields converted to Elements
        """
        if self.built:
            return

        for key in self.sorted_fields():
            field = self._fields[key]
            if field != self.root:
                if isinstance(field, XmlModel):
                    field.build_tree()
                    self.doc_root.append(field.doc_root)
                elif isinstance(field, list):
                    # we just allow XmlFields and XmlModels in the list
                    for item in field:
                        if isinstance(item, XmlField):
                            self.doc_root.append(item.element())
                        elif isinstance(item, XmlModel):
                            item.build_tree()
                            self.doc_root.append(item.doc_root)
                        item = None
                elif (field.parent or self.root.name) == self.root.name:
                    field = field.element(parent=self.doc_root)
                else:
                    nodes = [n for n in self.doc_root.iterdescendants(
                                            tag=field.parent)]
                    if nodes:
                        field = field.element(parent=nodes[0])
                    #else:
                    #    raise RuntimeError("No parent found!")
        self.built = True


    def __str__(self):
        return etree.tostring(self.doc_root)


    def __unicode__(self):
        return self.__str__()


