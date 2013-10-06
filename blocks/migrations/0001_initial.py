# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Promotable'
        db.create_table(u'blocks_promotable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, db_index=True)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('promoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'blocks', ['Promotable'])

        # Adding M2M table for field sites on 'Promotable'
        m2m_table_name = db.shorten_name(u'blocks_promotable_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('promotable', models.ForeignKey(orm[u'blocks.promotable'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['promotable_id', 'site_id'])

        # Adding model 'MenuTranslation'
        db.create_table(u'blocks_menu_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=200, blank=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['blocks.Menu'])),
        ))
        db.send_create_signal(u'blocks', ['MenuTranslation'])

        # Adding unique constraint on 'MenuTranslation', fields ['language_code', 'master']
        db.create_unique(u'blocks_menu_translation', ['language_code', 'master_id'])

        # Adding model 'Menu'
        db.create_table(u'blocks_menu', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('blocks.fields.OrderField')(default=0, db_index=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, db_index=True)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('blocks.fields.SlugURLField')(max_length=200, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, db_index=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['blocks.Menu'])),
        ))
        db.send_create_signal(u'blocks', ['Menu'])

        # Adding M2M table for field sites on 'Menu'
        m2m_table_name = db.shorten_name(u'blocks_menu_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('menu', models.ForeignKey(orm[u'blocks.menu'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['menu_id', 'site_id'])

        # Adding model 'Template'
        db.create_table(u'blocks_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'blocks', ['Template'])

        # Adding model 'PageTranslation'
        db.create_table(u'blocks_page_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['blocks.Page'])),
        ))
        db.send_create_signal(u'blocks', ['PageTranslation'])

        # Adding unique constraint on 'PageTranslation', fields ['language_code', 'master']
        db.create_unique(u'blocks_page_translation', ['language_code', 'master_id'])

        # Adding model 'Page'
        db.create_table(u'blocks_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, db_index=True)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('menu', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, db_index=True)),
            ('template_name', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('is_relative', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'blocks', ['Page'])

        # Adding M2M table for field sites on 'Page'
        m2m_table_name = db.shorten_name(u'blocks_page_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm[u'blocks.page'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['page_id', 'site_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'PageTranslation', fields ['language_code', 'master']
        db.delete_unique(u'blocks_page_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'MenuTranslation', fields ['language_code', 'master']
        db.delete_unique(u'blocks_menu_translation', ['language_code', 'master_id'])

        # Deleting model 'Promotable'
        db.delete_table(u'blocks_promotable')

        # Removing M2M table for field sites on 'Promotable'
        db.delete_table(db.shorten_name(u'blocks_promotable_sites'))

        # Deleting model 'MenuTranslation'
        db.delete_table(u'blocks_menu_translation')

        # Deleting model 'Menu'
        db.delete_table(u'blocks_menu')

        # Removing M2M table for field sites on 'Menu'
        db.delete_table(db.shorten_name(u'blocks_menu_sites'))

        # Deleting model 'Template'
        db.delete_table(u'blocks_template')

        # Deleting model 'PageTranslation'
        db.delete_table(u'blocks_page_translation')

        # Deleting model 'Page'
        db.delete_table(u'blocks_page')

        # Removing M2M table for field sites on 'Page'
        db.delete_table(db.shorten_name(u'blocks_page_sites'))


    models = {
        u'blocks.menu': {
            'Meta': {'object_name': 'Menu'},
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('blocks.fields.OrderField', [], {'default': '0', 'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['blocks.Menu']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'db_index': 'True', 'symmetrical': 'False'}),
            'slug': ('blocks.fields.SlugURLField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        u'blocks.menutranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'MenuTranslation', 'db_table': "u'blocks_menu_translation'"},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['blocks.Menu']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'blocks.page': {
            'Meta': {'ordering': "('url',)", 'object_name': 'Page'},
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'menu': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'db_index': 'True', 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        u'blocks.pagetranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'PageTranslation', 'db_table': "u'blocks_page_translation'"},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['blocks.Page']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'blocks.promotable': {
            'Meta': {'object_name': 'Promotable'},
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'promoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'db_index': 'True', 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'blocks.template': {
            'Meta': {'object_name': 'Template'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['blocks']