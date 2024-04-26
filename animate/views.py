from flask import Blueprint, render_template, url_for, request, session, flash, redirect
from .models import Cate, Product, Order
from datetime import datetime
from .forms import CheckoutForm
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    cates = Cate.query.order_by(Cate.name).all()
    return render_template('index.html', cates=cates)

@main_bp.route('/cates/<int:cateid>')
def catedetail(cateid):
    cates = Cate.query.filter(Product.cate_id==cateid).first()
    cateprod = Product.query.filter(Product.cate_id == cateid)
    return render_template('catedetail.html', cates = cates, prods = cateprod)

@main_bp.route('/prods/<int:productid>')
def productdetail(productid):
    prods = Product.query.get(productid)
    cates = Cate.query.filter(Cate.id == prods.cate_id).first()
    return render_template('productdetail.html', product=prods, cates = cates)


# Referred to as "Basket" to the user
@main_bp.route('/order', methods=['POST','GET'])
def order():
    product_id = request.values.get('product_id')

    # retrieve order if there is one
    if 'order_id'in session.keys():
        order = Order.query.get(session['order_id'])
        # order will be None if order_id stale
    else:
        # there is no order
        order = None

    # create new order if needed
    if order is None:
        order = Order(status = False, firstname='', surname='', email='', phone='', totalcost=0, date=datetime.now())
        try:
            db.session.add(order)
            db.session.commit()
            session['order_id'] = order.id
        except:
            print('failed at creating a new order')
            order = None
    
    # calcultate totalprice
    total_price = 0
    if order is not None:
        for prods in order.prods:
            total_price = total_price + prods.price
    
    # are we adding an item?
    if product_id is not None and order is not None:
        product = Product.query.get(product_id)
        if product not in order.prods:
            try:
                order.prods.append(product)
                db.session.commit()
            except:
                return 'There was an issue adding the item to your basket'
            return redirect(url_for('main.order'))
        else:
            flash('item already in basket')
            return redirect(url_for('main.order'))
    return render_template('order.html', order = order, total_price=total_price)

# Delete specific basket items
@main_bp.route('/deleteorderitem', methods=['POST'])
def deleteorderitem():
    id=request.form['id']
    if 'order_id' in session:
        order = Order.query.get_or_404(session['order_id'])
        product_to_delete = Product.query.get(id)
        try:
            order.prods.remove(product_to_delete)
            db.session.commit()
            return redirect(url_for('main.order'))
        except:
            return 'Problem deleting item from order'
    return redirect(url_for('main.order'))

# Scrap basket
@main_bp.route('/deleteorder')
def deleteorder():
    if 'order_id' in session:
        del session['order_id']
        flash('All items deleted')
    return redirect(url_for('main.index'))

@main_bp.route('/products')

def search():

    search = request.args.get('search')

    search = '%{}%'.format(search) # substrings will match

    product = Product.query.filter(Product.name.like(search)).all()

    return render_template('catedetail.html', prods=product)

@main_bp.route('/checkout', methods=['POST','GET'])
def checkout():
    form = CheckoutForm() 
    if 'order_id' in session:
        order = Order.query.get_or_404(session['order_id'])
       
        if form.validate_on_submit():
            order.status = True
            order.firstname = form.firstname.data
            order.surname = form.surname.data
            order.email = form.email.data
            order.phone = form.phone.data
            totalcost = 0
            for product in order.prods:
                totalcost = totalcost + product.price
            order.totalcost = totalcost
            order.date = datetime.now()
            try:
                db.session.commit()
                del session['order_id']
                flash('Thank you! One of our awesome team members will contact you soon...')
                return redirect(url_for('main.index'))
            except:
                return 'There was an issue completing your order'
    return render_template('checkout.html', form=form)

@main_bp.route('/sub', methods=['POST','GET'])
def sub():
    flash('Thank you to subscribe to our newsletter.')
    return redirect(url_for('main.index'))

@main_bp.route('/video')
def showVid():
    return render_template('video.html')