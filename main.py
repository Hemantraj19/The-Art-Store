from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    make_response,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from form import (
    UserLoginForm,
    UserRegisterForm,
    SellerLoginForm,
    SellerRegisterForm,
    AddItemForm,
    RatingReviewForm,
    AddressForm,
)
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from upload_to_firebase import UploadImage
import json


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = "dev"

bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

Base = declarative_base()

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
db.init_app(app)

firebase = UploadImage()


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user:
        return user
    else:
        seller = Seller.query.get(user_id)
        return seller


def user_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_seller:
            flash("You should be logged in to view the page.")
            return redirect(url_for("user_login"))
        return func(*args, **kwargs)

    return decorated_function


def seller_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_seller:
            flash("You should be logged in as seller to view the page.")
            return redirect(url_for("seller_login"))
        return func(*args, **kwargs)

    return decorated_function


class Item(db.Model):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(String, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    seller_id = Column(Integer, ForeignKey("seller.id"), nullable=False)
    images = db.relationship("Image", backref="item", lazy=True)


class Image(db.Model):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    @property
    def is_seller(self):
        return False


class Cart(db.Model):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    user = db.relationship("User", backref="cart", lazy=True)
    item = db.relationship("Item", backref="cart", lazy=True)


class Orders(db.Model):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    user = db.relationship("User", backref="order", lazy=True)
    item = db.relationship("Item", backref="order", lazy=True)


class Seller(UserMixin, db.Model):
    __tablename__ = "seller"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_num = Column(String, nullable=False)
    address = Column(String, nullable=False)
    password = Column(String, nullable=False)
    item = db.relationship("Item", backref="seller", lazy=True)

    @property
    def is_seller(self):
        return True


class Rating(db.Model):
    __tablename__ = "rating"
    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    comment = Column(Text, nullable=True)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="rating", lazy=True)
    item = db.relationship("Item", backref="rating", lazy=True)


class Address(db.Model):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    address = Column(Text, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    phn_no = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="address", lazy=True)


with app.app_context():
    db.create_all()


@app.before_request
def before_request():
    if "cart_count" not in session:
        session["cart_count"] = 0


@app.route("/")
def home():

    if current_user.is_seller:
        return redirect(url_for("seller_home"))

    items = db.session.execute(db.select(Item)).scalars().all()
    images = [
        db.session.execute(db.select(Image).where(Image.item_id == item.id))
        .scalars()
        .first()
        for item in items
    ]
    zipped_items = zip(items, images)

    if current_user.is_authenticated:
        session["cart_count"] = (
            db.session.query(Cart).filter(Cart.user_id == current_user.id).count()
        )

    return render_template(
        "index.html", zipped_items=zipped_items, current_user=current_user
    )


@app.route("/user-login", methods=["GET", "POST"])
def user_login():
    user_login_form = UserLoginForm()
    if user_login_form.validate_on_submit():
        email = user_login_form.email.data
        result = db.session.execute(db.Select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("Wrong email or password")
            return redirect(url_for("user_login"))
        elif not check_password_hash(user.password, user_login_form.password.data):
            flash("Wrong email or password")
            return redirect(url_for("user_login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("user-login.html", user_login_form=user_login_form)


@app.route("/user-register", methods=["GET", "POST"])
def user_register():
    user_register_form = UserRegisterForm()
    if user_register_form.validate_on_submit():
        result = db.session.execute(
            db.select(User).where(User.email == user_register_form.email.data)
        )
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("user_login"))

        new_user = User(
            name=user_register_form.name.data,
            email=user_register_form.email.data,
            password=generate_password_hash(
                user_register_form.password.data, method="scrypt", salt_length=16
            ),
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("user-register.html", user_register_form=user_register_form)


@app.route("/user-logout")
def user_logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/seller-home")
@seller_required
def seller_home():
    items = (
        db.session.execute(db.Select(Item).where(Item.seller_id == current_user.id))
        .scalars()
        .all()
    )
    images = []
    for item in items:
        image = db.session.execute(
            db.Select(Image).where(Image.item_id == item.id)
        ).scalar()
        images.append(image)
    zipped_items = zip(items, images)
    return render_template("seller-home.html", zipped_items=zipped_items)


@app.route("/seller-login", methods=["GET", "POST"])
def seller_login():
    seller_login_form = SellerLoginForm()
    if seller_login_form.validate_on_submit():
        email = seller_login_form.email.data
        result = db.session.execute(db.Select(Seller).where(Seller.email == email))
        seller = result.scalar()

        if not seller:
            flash("Wrong email or password")
            return redirect(url_for("seller_login"))
        elif not check_password_hash(seller.password, seller_login_form.password.data):
            flash("Wrong email or password")
            return redirect(url_for("seller_login"))
        else:
            login_user(seller)
            return redirect(url_for("seller_home"))
    return render_template("seller-login.html", seller_login_form=seller_login_form)


@app.route("/seller-register", methods=["GET", "POST"])
def seller_register():
    seller_register_form = SellerRegisterForm()
    if seller_register_form.validate_on_submit():

        result = db.session.execute(
            db.Select(Seller).where(Seller.email == seller_register_form.email.data)
        )
        seller = result.scalar()
        if seller:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("seller_login"))

        new_seller = Seller(
            name=seller_register_form.name.data,
            email=seller_register_form.email.data,
            phone_num=seller_register_form.phone_num.data,
            address=seller_register_form.address.data,
            password=generate_password_hash(
                seller_register_form.password.data, method="scrypt", salt_length=16
            ),
        )
        db.session.add(new_seller)
        db.session.commit()
        return redirect(url_for("seller_login"))
    return render_template(
        "seller-register.html", seller_register_form=seller_register_form
    )


@app.route("/seller-logout")
def seller_logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/add-item", methods=["GET", "POST"])
@seller_required
def add_item():
    add_item_form = AddItemForm()
    if add_item_form.validate_on_submit():
        new_item = Item(
            name=add_item_form.name.data,
            description=add_item_form.description.data,
            price=add_item_form.price.data,
            available_quantity=add_item_form.available_quantity.data,
            seller_id=current_user.id,
        )
        db.session.add(new_item)
        db.session.commit()
        images = add_item_form.images.data
        for image in images:
            url = firebase.get_img_url(image)
            new_image = Image(image_url=url, item_id=new_item.id)
            db.session.add(new_image)
            db.session.commit()

        return redirect(url_for("home"))

    return render_template("add-item.html", add_item_form=add_item_form)


@app.route("/view-art/<int:art_id>")
def view_art(art_id):
    art = db.get_or_404(Item, art_id)
    reviews = (
        db.session.execute(db.Select(Rating).where(Rating.item_id == art.id))
        .scalars()
        .all()
    )
    images = (
        db.session.execute(db.Select(Image).where(Image.item_id == art.id))
        .scalars()
        .all()
    )
    seller = db.session.execute(
        db.Select(Seller).where(Seller.id == art.seller_id)
    ).scalar()
    return render_template("view-art.html", art=art, images=images, seller=seller)


@app.route("/rating")
def rating():
    rating_review_form = RatingReviewForm()
    return render_template("rating.html", form=rating_review_form)


@app.route("/add-to-cart/<int:art_id>", methods=["POST"])
@user_required
def add_to_cart(art_id):
    print(request.form)
    cart_item = Cart(
        user_id=current_user.id,
        item_id=art_id,
        quantity=request.form.get("quantity"),
    )
    db.session.add(cart_item)
    db.session.commit()
    session["cart_count"] += 1
    return redirect(url_for("home"))


@app.route("/remove-from-cart/<int:item_id>")
def remove_from_cart(item_id):
    item = db.session.execute(db.Select(Cart).where(Cart.item_id == item_id)).scalar()
    db.session.delete(item)
    db.session.commit()
    session["cart_count"] -= 1
    return redirect(url_for("view_cart"))


@app.route("/buy-now/<int:art_id>")
@user_required
def buy_now(art_id):
    addresses = db.session.execute(
        db.Select(Address).filter(Address.user_id == current_user.id)
    ).scalars()
    image = db.session.execute(
        db.Select(Image).filter(Image.item_id == art_id)
    ).scalar()
    item = db.session.execute(db.Select(Item).where(Item.id == art_id)).scalar()
    seller = db.session.execute(
        db.Select(Seller).where(Seller.id == item.seller_id)
    ).scalar()
    return render_template(
        "buy-now.html",
        addresses=addresses,
        image=image,
        item=item,
        seller=seller,
        current_user=current_user,
    )


@app.route("/view-cart")
@user_required
def view_cart():
    cart_items = (
        db.session.execute(db.Select(Cart).where(Cart.user_id == current_user.id))
        .scalars()
        .all()
    )
    images = []
    items = []
    sellers = []
    quantity = []
    images_items_sellers_zipped = None
    total_price = 0.0
    for cart_item in cart_items:
        image = db.session.execute(
            db.Select(Image).where(Image.item_id == cart_item.item_id)
        ).scalar()
        images.append(image)
        item = db.session.execute(
            db.Select(Item).where(Item.id == cart_item.item_id)
        ).scalar()
        items.append(item)
        seller = db.session.execute(
            db.Select(Seller).where(Seller.id == item.seller_id)
        ).scalar()
        sellers.append(seller)
        quantity.append(cart_item.quantity)
        images_items_sellers_zipped = zip(images, items, sellers, quantity)
    for item, quant in zip(items, quantity):
        total_price += float(item.price) * quant
    return render_template(
        "cart.html",
        images_items_sellers_zipped=images_items_sellers_zipped,
        no_items=len(items),
        total_price=total_price,
    )


@app.route("/view-orders")
@user_required
def view_orders():
    return render_template("orders.html")


@app.route("/add-address", methods=["GET", "POST"])
@user_required
def add_address():
    form = AddressForm()
    if form.validate_on_submit():
        new_address = Address(
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            pincode=form.pincode.data,
            phn_no=form.phn_no.data,
            user_id=current_user.id,
        )
        db.session.add(new_address)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add-address.html", form=form)


@app.route("/buy-from/cart")
@user_required
def buy_from_cart():
    addresses = db.session.execute(
        db.Select(Address).filter(Address.user_id == current_user.id)
    ).scalars()
    cart_items = (
        db.session.execute(db.Select(Cart).where(Cart.user_id == current_user.id))
        .scalars()
        .all()
    )
    images = []
    items = []
    sellers = []
    images_items_sellers_zipped = None
    total_price = 0.0
    for cart_item in cart_items:
        image = db.session.execute(
            db.Select(Image).where(Image.item_id == cart_item.item_id)
        ).scalar()
        images.append(image)
        item = db.session.execute(
            db.Select(Item).where(Item.id == cart_item.item_id)
        ).scalar()
        items.append(item)
        seller = db.session.execute(
            db.Select(Seller).where(Seller.id == item.seller_id)
        ).scalar()
        sellers.append(seller)
        images_items_sellers_zipped = zip(images, items, sellers)
    for item in items:
        total_price += float(item.price)
    return render_template(
        "buy-from-cart.html",
        addresses=addresses,
        images_items_sellers_zipped=images_items_sellers_zipped,
        no_items=len(items),
        total_price=total_price,
    )


@app.route("/payment")
@user_required
def payment():
    return render_template("payment-page.html")


@app.route("/delete-item/<int:item_id>")
@seller_required
def delete_item(item_id):
    item = db.get_or_404(Item, item_id)
    images = db.session.execute(
        db.Select(Image).where(Image.item_id == item.id)
    ).scalars()
    cart_items = db.session.execute(
        db.Select(Cart).where(Cart.item_id == item.id)
    ).scalars()
    for image in images:
        db.session.delete(image)
    for cart in cart_items:
        db.session.delete(cart)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("seller_home"))


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
