from app import db
from app.models.customer import Customer
from app.models.video import Video
from app.models.rental import Rental
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask.helpers import make_response
import os
import requests

# set up blueprints
# wave 1 (customers & videos)
videos_bp = Blueprint("videos", __name__, url_prefix="/videos")
customers_bp = Blueprint("customers", __name__, url_prefix="/customers")
# wave 2 (rentals)
rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")

# helper function to check that customer/video ids are integers
def is_int(value):
    try:
        return int(value)
    except ValueError:
        return False
# **********************************************************
# Wave 1: CRUD (Create, Read, Update & Delete) for customer
# **********************************************************
@customers_bp.route("", methods=["POST"], strict_slashes=False)
def create_customer():
    try:
        customer_data = request.get_json()

        new_customer = Customer(name=customer_data["name"],
                                postal_code=customer_data["postal_code"],
                                phone=customer_data["phone"],
                                registered_at=datetime.now())
        db.session.add(new_customer)
        db.session.commit()

        return jsonify({
            "id": new_customer.customer_id
        }), 201
    except KeyError:
        return make_response({"details": "Invalid data"}, 400)

@customers_bp.route("", methods=["GET"], strict_slashes=False)
def get_customer():
    customer_name_from_url = request.args.get("name")
    # get customer by name
    if customer_name_from_url:
        customers = Customer.query.filter.by(name=customer_name_from_url)
    # get all customers
    else:
        customers = Customer.query.all()
    
    customers_response = []

    for customer in customers:
        customers_response.append(customer.to_json())
    
    return jsonify(customers_response), 200

@customers_bp.route("/<customer_id>", methods=["GET"], strict_slashes=False)
def get_one_customer(customer_id):
    if not is_int(customer_id):
        return {
            "message": f"ID {customer_id} must be an integer",
            "success": False
        }, 400
    
    customer = Customer.query.get(customer_id)

    if customer is None:
        return make_response("Customer does not exist", 404)
    else:
        return customer.to_json(), 200

@customers_bp.route("/<customer_id>", methods=["PUT"], strict_slashes=False)
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    customer_data = request.get_json()

    if customer is None:
        return make_response("Customer does not exist", 404)

    elif ("name" not in customer_data.keys() or
        "postal_code" not in customer_data.keys() or
        "phone" not in customer_data.keys()):
            return make_response({"error": "Bad Request"}, 400)

    elif customer:

        customer.name = customer_data["name"]
        customer.postal_code = customer_data["postal_code"]
        customer.phone = customer_data["phone"]
        
        db.session.add(customer)
        db.session.commit()

        return jsonify(customer.to_json()), 200


@customers_bp.route("/<customer_id>", methods=["DELETE"], strict_slashes=False)
def delete_customer(customer_id):

    customer = Customer.query.get(customer_id)

    if customer is None:
        return make_response("Customer does not exist", 404)
    else:
        db.session.delete(customer)
        db.session.commit()

        return jsonify({
            "id": customer.customer_id
        }), 200

# Wave 1: CRUD (Create, Read, Update & Delete) for video
@videos_bp.route("", methods=["POST"], strict_slashes=False)
def create_video():
    try:
        request_body = request.get_json()

        new_video = Video(title=request_body["title"],
                            release_date=request_body["release_date"],
                            total_inventory=request_body["total_inventory"])
        db.session.add(new_video)
        db.session.commit()

        return jsonify({
            "id": new_video.video_id
        }), 201
    
    except KeyError:
        return make_response({"details": "Invalid data"}, 400)

@videos_bp.route("", methods=["GET"], strict_slashes=False)
def get_video():
    video_title_from_url = request.args.get("title")
    # get video by title
    if video_title_from_url:
        videos = Video.query.filter.by(title=video_title_from_url)
    # get all videos
    else:
        videos = Video.query.all()
    
    video_response = []

    for video in videos:
        video_response.append(video.to_json())
    
    return jsonify(video_response), 200

@videos_bp.route("/<video_id>", methods=["GET"], strict_slashes=False)
def get_one_video(video_id):
    if not is_int(video_id):
        return {
            "message": f"ID {video_id} must be an integer",
            "success": False
        }, 400
    
    video = Video.query.get(video_id)

    if video is None:
        return make_response("Video does not exist", 404)
    else:
        return video.to_json(),200

@videos_bp.route("/<video_id>", methods=["PUT"], strict_slashes=False)
def update_video(video_id):

    video = Video.query.get(video_id)
    if video is None:
        return("", 404)
    elif video:
        video_data = request.get_json()

        video.title = video_data["title"]
        video.release_date = video_data["release_date"]
        video.total_inventory = video_data["total_inventory"]
        
        db.session.add(video)
        db.session.commit()

        return jsonify(video.to_json()), 200
    else:
        return make_response({"error": "Bad Request"}, 400)

@videos_bp.route("/<video_id>", methods=["DELETE"], strict_slashes=False)
def delete_video(video_id):

    video = Video.query.get(video_id)

    if video is None:
        return make_response("Video does not exist", 404)
    else:
        db.session.delete(video)
        db.session.commit()

        return jsonify({
            "id": video.video_id
        }), 200

# **********************************
# Wave 2 routes (rental) POST & GET
# **********************************
@rentals_bp.route("/check-out", methods=["POST"], strict_slashes=False)
def initiate_rental():
    rental_data = request.get_json()

    try:
        # converts video_id & customer_id strings into an integers (because Postman is dumb lol)
        video_id = int(rental_data["video_id"])
        customer_id = int(rental_data["customer_id"])
    except ValueError or KeyError:
        return make_response({"error": "Bad Request"}, 400)
    
    # checks if inventory
    num_vids = Video.query.get(rental_data["video_id"]).index_available_inventory()
    if num_vids == 0:
        return make_response({"error": "Bad Request"}, 400)
    
    # generates video and customer instances
    customer = Customer.query.get(rental_data["customer_id"])
    video = Video.query.get(rental_data["video_id"])
    
    # Initialize rental - needs customer_id & video_id
    new_rental = Rental(customer_id = rental_data["customer_id"],
                        video_id = rental_data["video_id"])

    # add to database & commit
    db.session.add(new_rental)
    db.session.commit()

    # return dictionary containing appropriate key-value pairs
    return {
        "customer_id": customer.customer_id,
        "video_id": video.video_id,
        "due_date": new_rental.due_date,
        "videos_checked_out_count": customer.index_checked_out(),
        "available_inventory": video.index_available_inventory()
    }, 200

@rentals_bp.route("/check-in", methods=["POST"], strict_slashes=False)
def return_rental():
    rental_data = request.get_json()

    try:
    # converts video_id & customer_id strings into an integers (because Postman is dumb lol)
        video_id = int(rental_data["video_id"])
        customer_id = int(rental_data["customer_id"])
    except ValueError or KeyError:
        return make_response({"error": "Bad Request"}, 400)

    # initializes rental
    rental = Rental.query.filter(Rental.customer_id == rental_data["customer_id"], Rental.video_id == rental_data["video_id"]).first()

    # checks if rental exists
    if rental is None:
        return make_response("Rental does not exist", 400)
    
    # initializes customer
    customer = Customer.query.get(rental_data["customer_id"])

    # grabs video list from many-to-many relationship
    video_list = customer.videos

    # removes video from video_list if it matches the rental being checked-in
    for video in video_list:
        if video.video_id == rental_data["video_id"]:
            video_list.remove(video)
    
    db.session.commit()

    video = Video.query.get(rental_data["video_id"])

    return {
        "customer_id": customer.customer_id,
        "video_id": video.video_id,
        "videos_checked_out_count": customer.index_checked_out(),
        "available_inventory": video.index_available_inventory()
    }, 200

#  Wave 2 GET routes
@customers_bp.route("/<customer_id>/rentals", methods=["GET"], strict_slashes=False)
def get_rental_customers(customer_id):

    if not is_int(customer_id):
        return ("Customer ID needs to be an integer!", 400)
    
    rentals = Rental.query.filter(Rental.customer_id == customer_id)

    if rentals is None:
        return make_response("Rental does not exist", 404)
    
    rental_list = []

    for rental in rentals:
        video = Video.query.get(rental.video_id)
        rental_list.append(
            {"release_date": video.release_date,
            "title": video.title,
            "due_date":rental.due_date}
        )
    return jsonify(rental_list), 200

@videos_bp.route("/<video_id>/rentals", methods=["GET"], strict_slashes=False)
def get_video_customers(video_id):

    if not is_int(video_id):
        return ("Video ID needs to be an integer!", 400)
    
    rentals = Rental.query.filter(Rental.video_id == video_id)

    if rentals is None:
        return make_response("Rental does not exist", 404)

    rental_list = []

    for rental in rentals:
        customer = Customer.query.get(rental.customer_id)
        rental_list.append(
            {"due_date": rental.due_date,
            "name": customer.name,
            "phone": customer.phone,
            "postal_code": customer.postal_code}
        )
    
    return jsonify(rental_list), 200