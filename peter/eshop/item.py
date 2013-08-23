from five import grok

from z3c.form import group, field
from z3c.form import button
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder 
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
from plone.directives import dexterity, form
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from plone.app.textfield import RichText


from peter.eshop import MessageFactory as _

# Interface class; used to define content-type schema.

class IItem(form.Schema, IImageScaleTraversable):
    """
    An item inside E-Shop
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/item.xml to define the content type.

    #form.model("models/item.xml") price = schema.Float(title = _(u"Price"), min=0.0)


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Item(Container):
    grok.implements(IItem)

    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# item_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class SampleView(grok.View):
    """ sample view class """

    grok.context(IItem)
    grok.require('zope2.View')

    # grok.name('view')

    # Add view methods here

from plone.supermodel import model
class IAddItemToCart(model.Schema):

    count = schema.Int(title = _(u"Count"), min=0)

class AddItemToCart(form.SchemaForm):
    grok.context(IItem)
    grok.require('zope2.View')
    grok.name('add-item-to-cart')

    schema = IAddItemToCart
    ignoreContext = True

    def update(self):
        smd = self.context.session_data_manager
        session = smd.getSessionData(create=True)
        cart = session.get('cart',{})
        self.schema['count'].default = cart.get(self.context,0)
        super(AddItemToCart, self).update()

    @button.buttonAndHandler(_(u'Add'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        smd = self.context.session_data_manager
        session = smd.getSessionData(create=True)
        cart = session.get('cart',{})
        cart[self.context] = data['count']
        session.set('cart',cart)
        from Products.statusmessages.interfaces import IStatusMessage
        message = IStatusMessage(self.request)
        message.addStatusMessage("Item added to cart", type="info")
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

from Products.CMFCore.interfaces import ISiteRoot

class CartView(grok.View):
    """ sample view class """

    grok.context(ISiteRoot)
    grok.require('zope2.View')
    grok.name('cart')
    grok.template('cartview')

    def update(self):
        smd = self.context.session_data_manager
        session = smd.getSessionData(create=True)
        self.cart = session.get('cart',{})

class IOrderForm(model.Schema):
    name = schema.Text(title = _(u"Name"))
    email = schema.Text(title = _(u"E-mail"))

class OrderedForm(form.SchemaForm):
    grok.context(ISiteRoot)
    grok.require('zope2.View')
    grok.name('ordercart')
    schema = IOrderForm
    ignoreContext = True

    @button.buttonAndHandler(_(u'Order'))
    def handleOrder(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        smd = self.context.session_data_manager
        session = smd.getSessionData(create=True)
        cart = session.get('cart',{})
        from Products.statusmessages.interfaces import IStatusMessage
        message = IStatusMessage(self.request)
        message.addStatusMessage("You have ordered %s"%", ".join(
            [i.title for i in cart.keys()]
            ), type="info")
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

