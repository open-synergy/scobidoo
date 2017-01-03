# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import io
import logging

from openerp import api, fields, models, _

from sismic.exceptions import StatechartError
from sismic import io as sismic_io


_logger = logging.getLogger(__name__)


class Statechart(models.Model):

    _name = 'statechart'
    _description = 'Statechart'

    name = fields.Char(
        related='model_id.model',
        readonly=True)
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required='True',
        ondelete='restrict')
    yaml = fields.Text(
        help="YAML representation of the state chart."
             "Currently it is the input, to become a computed field "
             "from a future record-based reprensentation of "
             "the statechart.")

    _sql_constraint = [
        ('unique_model_id',
         'unique(model_id)',
         u'There can be at most one statechart per model')
    ]

    @api.multi
    def get_statechart(self):
        self.ensure_one()
        _logger.debug("loading statechart model for %s", self)
        with io.StringIO(self.yaml) as f:
            try:
                return sismic_io.import_from_yaml(f)
            except StatechartError:
                # TODO better error message
                raise

    # TODO ormcache
    @api.model  
    def statechart_for_model(self, model_name):
        """Load and parse the statechart for an Odoo model."""
        statechart = self.search([('model_id.model', '=', model_name)])
        if not statechart:
            return
        return statechart.get_statechart()