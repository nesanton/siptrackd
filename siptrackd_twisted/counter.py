from twisted.web import xmlrpc

from siptrackdlib import counter

from siptrackd_twisted import helpers
from siptrackd_twisted import gatherer
from siptrackd_twisted import baserpc

class CounterRPC(baserpc.BaseRPC):
    node_type = 'counter'

    @helpers.ValidateSession()
    def xmlrpc_add(self, session, parent_oid):
        """Create a new counter."""
        parent = self.object_store.getOID(parent_oid, user = session.user)
        obj = parent.add(session.user, 'counter')
        return obj.oid

    @helpers.ValidateSession()
    def xmlrpc_set(self, session, oid, value):
        """Set a counters value."""
        counter = self.getOID(session, oid)
        counter.set(value)
        return value

    @helpers.ValidateSession()
    def xmlrpc_get(self, session, oid):
        """Get a counters value."""
        counter = self.getOID(session, oid)
        return counter.get()

    @helpers.ValidateSession()
    def xmlrpc_inc(self, session, oid):
        """Increase a counters value."""
        counter = self.getOID(session, oid)
        counter.inc()
        return counter.get()

class CounterLoopRPC(baserpc.BaseRPC):
    node_type = 'counter loop'

    @helpers.ValidateSession()
    def xmlrpc_add(self, session, parent_oid, values):
        """Create a new counter."""
        parent = self.object_store.getOID(parent_oid, user = session.user)
        obj = parent.add(session.user, 'counter loop', values)
        return obj.oid

    @helpers.ValidateSession()
    def xmlrpc_set(self, session, oid, value):
        """Set a counters value."""
        counter = self.getOID(session, oid)
        counter.set(value)
        return value

    @helpers.ValidateSession()
    def xmlrpc_get(self, session, oid):
        """Get a counters value."""
        counter = self.getOID(session, oid)
        return counter.get()

    @helpers.ValidateSession()
    def xmlrpc_inc(self, session, oid):
        """Increase a counters value."""
        counter = self.getOID(session, oid)
        counter.inc()
        return counter.get()

    @helpers.ValidateSession()
    def xmlrpc_set_values(self, session, oid, values):
        """Set a looping counters values."""
        counter = self.getOID(session, oid)
        counter.setValues(values)
        return True

def counter_data_extractor(node, user):
    return [node.get()]

def counter_loop_data_extractor(node, user):
    return [node.get(), node.getValues()]

gatherer.node_data_registry.register(counter.Counter,
        counter_data_extractor)
gatherer.node_data_registry.register(counter.CounterLoop,
        counter_loop_data_extractor)

