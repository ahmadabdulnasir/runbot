import logging
import re
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Dockerfile(models.Model):
    _name = 'runbot.dockerfile'
    _description = "Dockerfile"

    name = fields.Char('Dockerfile name', required=True, unique=True, help="Name of Dockerfile")
    image_tag = fields.Char(compute='_compute_image_tag', store=True)
    template_id = fields.Many2one('ir.ui.view', string='Docker Template', domain=[('type', '=', 'qweb')], context={'default_type': 'qweb', 'default_arch_base': '<t></t>'})
    arch_base = fields.Text(related='template_id.arch_base', readonly=False)
    dockerfile = fields.Text(compute='_compute_dockerfile')
    to_build = fields.Boolean('Default', help='Default Dockerfile', default=False)
    version_ids = fields.One2many('runbot.version', 'dockerfile_id', string='Versions')
    description = fields.Text('Description')
    view_ids = fields.Many2many('ir.ui.view', compute='_compute_view_ids')

    @api.depends('template_id')
    def _compute_dockerfile(self):
        for rec in self:
            res = rec.template_id.render().decode() if rec.template_id else ''
            rec.dockerfile = re.sub(r'^\s*$', '', res, flags=re.M).strip()

    @api.depends('name')
    def _compute_image_tag(self):
        for rec in self:
            if rec.name:
                rec.image_tag = 'odoo:%s' % re.sub(r'[ /:\(\)\[\]]', '', rec.name)

    @api.depends('template_id')
    def _compute_view_ids(self):
        for rec in self:
            keys = re.findall(r'<t.+t-call="(.+)".+', rec.arch_base)
            rec.view_ids = self.env['ir.ui.view'].search([('type', '=', 'qweb'), ('key', 'in', keys)]).ids
