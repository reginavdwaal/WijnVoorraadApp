class MyDBRouter(object):

    route_conv_app_labels = {"ouddb"}

    def db_for_read(self, model, **hints):

        if model._meta.app_label in self.route_conv_app_labels:
            return "oudwijndb"
        return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label in self.route_conv_app_labels:
            return "oudwijndb"
        return None

    def allow_relation(self, obj1, obj2, **hints):

        if (
            obj1._meta.app_label in self.route_conv_app_labels
            and obj2._meta.app_label in self.route_conv_app_labels
        ):
            return True
        elif (
            obj1._meta.app_label not in self.route_conv_app_labels
            and obj2._meta.app_label not in self.route_conv_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.route_conv_app_labels:
            return db == "oudwijndb"
        return None
