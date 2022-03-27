from snapsettings import app

class Handler():
    def gtk_widget_destroy(self, *args):
        app.app.quit()

    def on_switch_metered_state_set(self, *args):
        if args[1] == True:
            state = 'null'
        elif args[1] == False:
            state = 'hold'
        app.app.set_metered_handling(state)

    def on_checkbox_metered_toggled(self, *args):
        state = args[0].get_active()
        if app.app.connection == '--':
            item = app.app.builder.get_object('checkbox_metered')
            item.set_active(False)
            return
        app.app.set_metered_status(app.app.connection, state)

    def on_timer_apply_clicked(self, *args):
        input_obj = args[0]
        suggested_obj = app.app.builder.get_object('timer_suggested')
        if input_obj.get_text():
            input = input_obj.get_text()
        else:
            input = suggested_obj.get_text()
            input_obj.set_text(input)
        app.app.set_refresh_timer(input)
        # Update next refresh time text.
        app.app.update_next_refresh_text()

    def on_revs_kept_value_changed(self, *args):
        revs = int(args[0].get_value())
        app.app.set_revisions_kept(revs)
