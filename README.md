# Alison Mungall's blog (amblog)

[Link to the site](https://alison-mungall.co.uk/)

## Overview

This project uses the Django web framework and has been deployed using a variety
of AWS services. Below are some highlights.

## Website Features
At a high level, the website is a blog that allows select users (staff) to post
text and images. Published posts can be commented on by authenticated visitors
and staff. Some specific features include:
-   **Search/sort capability:** The site allows the user to search and sort list
    views (drafts, posts and topics) using a search bar. For example, see
    class SearchView in
    [views.py](blog/views.py).
-   **Saving images in PK folder:** The site saves images uploaded by staff in
    directories that includes the post PK (primary key). As the post PK is
    assigned by the database, this requires saving the post and then moving
    the image into a new directory. See class Post in
    [models.py](blog/models.py).
-   **Error report emails:** The site will email the site admin if there are
    server or broken link errors.
-   **Social login:** The site uses
    [Python Social Auth](https://github.com/python-social-auth) for user login.
    LinkedIn was chosen as the social site due to this site being a
    professional blog, but more social sites may be added in the future.
-   **Rich text editor:** The site uses
    [Django CKEditor](https://github.com/django-ckeditor/django-ckeditor) to
    give staff full text editing capabilities.

## AWS Services
The AWS services primarily used are:
-   **Elastic Beanstalk:** Used to automatically handle deployment, capacity
    provisioning, load balancing, automatic scaling, and health monitoring.
-   **Amazon S3:** Used for storing user-uploaded images.
-   **Amazon RDS:** Used for the site database. Database engine: PostgreSQL.
-   **Route 53:** Used for the site DNS server.

## Security
To minimise the risk of losing personal data, and to comply
with GDPR, the site stores the minimum amount of data to be functional.
Regardless, the following measures have been taken to ensure the site
is secure:
-   **Argon2:** Used as the password hasher.
-   **Amazon EC2 Security Groups:** Used as virtual firewalls to control
    traffic to each instance. Public access is restricted to the load
    balancer only.
-   **HTTPS:** The load balancer redirects HTTP requests to HTTPS
    ensuring encrypted traffic only.
-   **VPC:** All instances are in one VPC and the database is
    on a non-routable subnet and is not public.
