from itertools import chain

from django import forms
from django.conf import settings
from django.forms.widgets import SelectMultiple
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils import simplejson as json

def get_doc(node, values):
    if hasattr(node, "get_doc"):
        return node.get_doc(values)
    if hasattr(node, "name"):
        name = node.name
    else:
        name = unicode(node)
    doc = {"title": name, "key": node.pk}
    if str(node.pk) in values:
        doc['select'] = True
        doc['expand'] = True
    return doc

def get_tree(nodes, values):
    parent = {}
    parent_level = 0
    stack = []
    results = []

    def add_doc(node, parent, parent_level):
        if node.level == parent_level:
            if node.level == 0:
                parent = get_doc(node, values)
                results.append(parent)
            else:
                prev_parent = parent
                parent_level -= 1
                parent = stack.pop()
                if prev_parent.get('expand', False):
                    parent['expand'] = True

        if node.level == parent_level + 2:
            stack.append(parent)
            parent_level += 1
            parent = parent['children'][-1]

        if node.level == parent_level + 1:
            children = parent.get('children', [])
            doc = get_doc(node, values)
            children.append(doc)
            if doc.get('select', False):
                parent['expand'] = True
            parent['children'] = children
        return (parent, parent_level)

    for node in nodes:
        parent, parent_level = add_doc(node, parent, parent_level)

    return results


class DynatreeWidget(SelectMultiple):
    def __init__(self, attrs=None, choices=(), queryset=None, select_mode=2):
        super(DynatreeWidget, self).__init__(attrs, choices)
        self.queryset = queryset
        self.select_mode = select_mode

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        if has_id:
            output = [u'<div id="%s"></div>' % attrs['id']]
        else:
            output = [u'<div></div>']
        if has_id:
            output.append(u'<ul class="dynatree_checkboxes" id="%s_checkboxes">' % attrs['id'])
        else:
            output.append(u'<ul class="dynatree_checkboxes">')
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], option_value))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(
                u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label)
            )
        output.append(u'</ul>')
        output.append(u'<script type="text/javascript">')
        if has_id:
            output.append(u'var dynatree_data_%s = %s;' % (
                attrs['id'],
                json.dumps(get_tree(self.queryset, str_values))
            ))
            output.append(
                """
                $(function() {
                    $("#%(id)s").dynatree({
                        checkbox: true,
                        selectMode: %(select_mode)d,
                        children: dynatree_data_%(id)s,
                        debugLevel: %(debug)d,
                        onSelect: function(select, node) {
                            $('#%(id)s_checkboxes').find('input[type=checkbox]').removeAttr('checked');
                            var selNodes = node.tree.getSelectedNodes();
                            var selKeys = $.map(selNodes, function(node){
                                   $('#%(id)s_' + (node.data.key)).attr('checked', 'checked');
                                   return node.data.key;
                            });
                        },
                        onClick: function(node, event) {
                            if( node.getEventTargetType(event) == "title" )
                                node.toggleSelect();
                        },
                        onKeydown: function(node, event) {
                            if( event.which == 32 ) {
                                node.toggleSelect();
                                return false;
                            }
                        }
                    });
                });
                """ % {
                    'id': attrs['id'],
                    'debug': settings.DEBUG and 1 or 0,
                    'select_mode': self.select_mode,
                }
            );
        output.append(u'</script>')
        return mark_safe(u'\n'.join(output))

    class Media:
        css = {
            'all': ('dynatree/skin/ui.dynatree.css',)
        }
        js = ('dynatree/jquery.dynatree.min.js',)
