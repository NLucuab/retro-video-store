from app import db
from app.models.customer import Customer
from app.models.video import Video
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask.helpers import make_response
import os
import requests

# set up blueprints
videos_bp = Blueprint("videos", __name__, url_prefix="/videos")
customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

# helper function to check that customer/video ids are integers
def is_int(value):
    try:
        return int(value)
    except ValueError:
        return False

# Wave 1: CRUD (Create, Read, Update & Delete) for customer
@customers_bp.route("", methods=["POST"], strict_slashes=False)
def create_customer():
    try:
        request_body = request.get_json()

        new_customer = Customer(name=request_body["name"],
                                postal_code=request_body["postal_code"],
                                phone=request_body["phone"],
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

    if customer:
        customer_data = request.get_json()

        customer.name = customer_data["name"]
        customer.postal_code = customer_data["postal_code"]
        customer.phone = customer_data["phone"]
        
        db.session.commit()

        return jsonify(customer.to_json()), 200
    else:
        return make_response({"error": "Bad Request"}, 400)

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
@videos_bp.route("/<video_id>", methods=["POST"], strict_slashes=False)
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

@videos_bp.route("/<video_id>", methods=["GET"], strict_slashes=False)
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

    if video:
        video_data = request.get_json()

        video.title = video_data["title"]
        video.release_date = video_data["release_date"]
        video.total_inventory = video_data["total_inventory"]
        
        db.session.commit()

        return jsonify(video.to_json()), 200
    elif video is None:
        return("", 404)
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