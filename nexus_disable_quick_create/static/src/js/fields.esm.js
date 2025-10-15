/** @odoo-module **/

import {Many2OneField} from "@web/views/fields/many2one/many2one_field";
import {patch} from "@web/core/utils/patch";
import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";

patch(Many2OneField.prototype, {
    defaultProps: {
        ...Many2OneField.defaultProps,
        canQuickCreate: false,
        canCreateEdit:false,
        canCreate:false,
        quick_create: false,
        no_quick_create: true,
        no_create_edit:true,

    },
    setup() {
        this.props.canQuickCreate = false;
        this.props.canCreate = false;
        this.props.canCreateEdit = false;
        super.setup();
    },
    computeActiveActions(props) {
        super.computeActiveActions(props);
        const activeActions = this.state.activeActions;
        activeActions.create = false;
        activeActions.createEdit = false;
    },

    extractProps({attrs}) {
        const props = super.extractProps(...arguments);
        //User want to use optional-> open command this
        //if (attrs.options.no_quick_create === undefined) props.canQuickCreate = false;
        //if (attrs.options.no_create === undefined) props.canCreate = false;
        //if (attrs.options.no_create_edit === undefined) props.canCreateEdit = false;
        props.canCreate = false;
        props.canQuickCreate = false;
        props.canCreateEdit = false;

        return props;
    },
});

patch(Many2ManyTagsField.prototype, {
    defaultProps: {
        ...Many2ManyTagsField.defaultProps,
        canQuickCreate: false,
        canCreateEdit:false,
        canCreate:false,
        quick_create: false,
        no_quick_create: true,
        no_create_edit:true,

    },
    setup() {
        this.props.canQuickCreate = false;
        this.props.canCreate = false;
        this.props.canCreateEdit = false;
        super.setup();
    },

    extractProps({attrs}) {
        const props = super.extractProps(...arguments);
        //User want to use optional-> open command this
        //if (attrs.options.no_quick_create === undefined) props.canQuickCreate = false;
        //if (attrs.options.no_create === undefined) props.canCreate = false;
        //if (attrs.options.no_create_edit === undefined) props.canCreateEdit = false;
        props.canCreate = false;
        props.canQuickCreate = false;
        props.canCreateEdit = false;

        return props;
    },
});
