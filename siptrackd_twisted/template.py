from twisted.web import xmlrpc
from twisted.internet import threads

from siptrackdlib import template

from siptrackd_twisted import helpers
from siptrackd_twisted import gatherer
from siptrackd_twisted import errors
from siptrackd_twisted import baserpc

class TemplateRPC(baserpc.BaseRPC):
    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_suggest_templates(self, base_oid, template_class):
        """Suggest available device templates for a node."""
        base_node = self.object_store.getOID(base_oid, user = self.user)
        oids = [tmpl.oid for tmpl in \
                template.suggest_templates(base_node, template_class)]
        return oids

class BaseTemplateRPC(baserpc.BaseRPC):
    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, inheritance_only,
            inherited_templates):
        """Create a new template."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        inherited_templates = [self.object_store.getOID(oid, user = self.user) for oid in \
                inherited_templates]
        obj = parent.add(self.user, self.node_type, inheritance_only,
                inherited_templates)
        return obj.oid

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_apply(self, oid, apply_oid, arguments = {}, overwrite = False,
            skip_rules = []):
        """Apply a template to a node."""
        template = self.getOID(oid)
        apply_node = self.object_store.getOID(apply_oid, user = self.user)
        skip_rules = [self.object_store.getOID(rule, user = self.user) for rule in skip_rules]
        # Disable threaded version, for now.
        template.apply(apply_node, arguments, overwrite, skip_rules, self.user)
        return True
#        user = self.user
#        return threads.deferToThread(template.apply, apply_node, arguments, overwrite, skip_rules, user)

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_combined_rules(self, oid):
        """Return a list of combined rules for a template."""
        template = self.getOID(oid)
        match_oids = []
        listcreator = gatherer.ListCreator(self.object_store, self.user)
        for rule in template.listCombinedRules():
            listcreator.build(rule, 0, include_parents = True,
                include_associations = False, include_references = False)
            match_oids.append(rule.oid)

        return [listcreator.prepared_data, match_oids]

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_suggest_templates(self, base_oid):
        """Suggest available device templates for a node."""
        base_node = self.object_store.getOID(base_oid, user = self.user)
        oids = [tmpl.oid for tmpl in \
                template.suggest_templates(base_node, self.node_type)]
        return oids

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_set_inheritance_only(self, oid, inheritance_only):
        tmpl = self.getOID(oid)
        tmpl.inheritance_only.set(inheritance_only)
        return True

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_set_inherited_templates(self, oid, inherited_templates):
        node = self.getOID(oid)
        inherited_templates = [self.object_store.getOID(oid, user = self.user) for oid in inherited_templates]
        node.inherited_templates.set(inherited_templates)
        return True

class DeviceTemplateRPC(BaseTemplateRPC):
    node_type = 'device template'

class NetworkTemplateRPC(BaseTemplateRPC):
    node_type = 'network template'

class TemplateRuleRPC(baserpc.BaseRPC):
    pass

class TemplateRulePasswordRPC(baserpc.BaseRPC):
    node_type = 'template rule password'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, username, description, key_oid):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, 'template', user = self.user)
        key = None
        if len(key_oid) > 0:
            key = self.object_store.getOID(key_oid, 'password key', user = self.user)
        obj = parent.add(self.user, 'template rule password', username, description, key)
        return obj.oid

class TemplateRuleAssignNetworkRPC(baserpc.BaseRPC):
    node_type = 'template rule assign network'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, 'template', user = self.user)
        obj = parent.add(self.user, 'template rule assign network')
        return obj.oid

class TemplateRuleSubdeviceRPC(baserpc.BaseRPC):
    node_type = 'template rule subdevice'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, num_devices, device_template_oid,
            sequence_offset):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        device_template = None
        if device_template_oid:
            device_template = self.object_store.getOID(device_template_oid,
                    ['device template'], user = self.user)
        obj = parent.add(self.user, 'template rule subdevice', num_devices,
            device_template, sequence_offset)
        return obj.oid

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_set_num_devices(self, oid, num_devices):
        tmpl = self.getOID(oid)
        tmpl.num_devices.set(num_devices)
        return True

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_set_device_template(self, oid, device_template_oid):
        rule = self.getOID(oid)
        tmpl = None
        if device_template_oid:
            tmpl = self.object_store.getOID(device_template_oid,
                    'template', user = self.user)
        rule.device_template.set(tmpl)
        return True

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_set_sequence_offset(self, oid, sequence_offset):
        tmpl = self.getOID(oid)
        tmpl.sequence_offset.set(sequence_offset)
        return True

class TemplateRuleTextRPC(baserpc.BaseRPC):
    node_type = 'template rule text'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, attr_name, versions):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule text', attr_name, versions)
        return obj.oid

class TemplateRuleFixedRPC(baserpc.BaseRPC):
    node_type = 'template rule fixed'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, attr_name, value, variable_expansion,
            versions):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule fixed', attr_name, value,
                variable_expansion, versions)
        return obj.oid

class TemplateRuleRegmatchRPC(baserpc.BaseRPC):
    node_type = 'template rule regmatch'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, attr_name, regexp, versions):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule regmatch', attr_name, regexp, versions)
        return obj.oid

class TemplateRuleBoolRPC(baserpc.BaseRPC):
    node_type = 'template rule bool'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, attr_name, default_value, versions):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule bool', attr_name, default_value,
                versions)
        return obj.oid

class TemplateRuleIntRPC(baserpc.BaseRPC):
    node_type = 'template rule int'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, attr_name, default_value, versions):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule int', attr_name, default_value,
                versions)
        return obj.oid

class TemplateRulePasswordRPC(baserpc.BaseRPC):
    node_type = 'template rule password'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, username, description, key_oid):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        key = None
        if len(key_oid) > 0:
            key = self.object_store.getOID(key_oid, user = self.user)
        obj = parent.add(self.user, 'template rule password', username, description, key)
        return obj.oid

class TemplateRuleAssignNetworkRPC(baserpc.BaseRPC):
    node_type = 'template rule assign network'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule assign network')
        return obj.oid

class TemplateRuleDeleteAttributeRPC(baserpc.BaseRPC):
    node_type = 'template rule delete attribute'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, attr_name):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule delete attribute', attr_name)
        return obj.oid

class TemplateRuleFlushNodesRPC(baserpc.BaseRPC):
    node_type = 'template rule flush nodes'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, include, exclude):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule flush nodes', include, exclude)
        return obj.oid

class TemplateRuleFlushAssociationsRPC(baserpc.BaseRPC):
    node_type = 'template rule flush associations'

    @helpers.error_handler
    @helpers.validate_session
    def xmlrpc_add(self, parent_oid, include, exclude):
        """Create a new template rule."""
        parent = self.object_store.getOID(parent_oid, user = self.user)
        obj = parent.add(self.user, 'template rule flush associations', include, exclude)
        return obj.oid

def template_data_extractor(node, user):
    inherited_templates = [i_node.oid for i_node in \
            node.inherited_templates.get()]
    return [node.inheritance_only.get(),
            inherited_templates]

def template_rule_password_data_extractor(node, user):
    key = ''
    if node.key.get():
        key = node.key.get().oid
    return [node.username.get(), node.description.get(), key]

def template_rule_subdevice_data_extractor(node, user):
    device_template = ''
    if node.device_template.get():
        device_template = node.device_template.get().oid
    return [node.num_devices.get(), device_template,
            node.sequence_offset.get()]

def template_rule_text_data_extractor(node, user):
    return [node.attr_name.get(), node.versions.get()]

def template_rule_fixed_data_extractor(node, user):
    return [node.attr_name.get(), node.value.get(),
            node.variable_expansion.get(), node.versions.get()]

def template_rule_regmatch_data_extractor(node, user):
    return [node.attr_name.get(), node.regexp.get(), node.versions.get()]

def template_rule_bool_data_extractor(node, user):
    return [node.attr_name.get(), node.default_value.get(),
            node.versions.get()]

def template_rule_int_data_extractor(node, user):
    return [node.attr_name.get(), node.default_value.get(),
            node.versions.get()]

def template_rule_delete_attribute_data_extractor(node, user):
    return [node.attr_name.get()]

def template_rule_password_data_extractor(node, user):
    key = ''
    if node.key.get():
        key = node.key.get().oid
    return [node.username.get(), node.description.get(), key]

def template_rule_flush_nodes_data_extractor(node, user):
    return [node.include.get(), node.exclude.get()]

def template_rule_flush_associations_data_extractor(node, user):
    return [node.include.get(), node.exclude.get()]

gatherer.node_data_registry.register(template.DeviceTemplate,
        template_data_extractor)
gatherer.node_data_registry.register(template.NetworkTemplate,
        template_data_extractor)

gatherer.node_data_registry.register(template.TemplateRulePassword,
        template_rule_password_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleAssignNetwork,
        gatherer.no_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleSubdevice,
        template_rule_subdevice_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleText,
        template_rule_text_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleFixed,
        template_rule_fixed_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleRegmatch,
        template_rule_regmatch_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleBool,
        template_rule_bool_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleInt,
        template_rule_int_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleDeleteAttribute,
        template_rule_delete_attribute_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleFlushNodes,
        template_rule_flush_nodes_data_extractor)
gatherer.node_data_registry.register(template.TemplateRuleFlushAssociations,
        template_rule_flush_associations_data_extractor)