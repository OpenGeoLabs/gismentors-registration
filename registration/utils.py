import os


def get_certificate_templates():
    this_dir = os.path.dirname(
        os.path.abspath(__file__))

    certficates_dir = os.path.abspath(
        os.path.join(this_dir, "..", "certifikat", "templates"))
    certificates = os.listdir(certficates_dir)

    certificates = ((cert, cert) for cert in certificates)

    return certificates

def get_certificate_template(course_event):

    this_dir = os.path.dirname(
        os.path.abspath(__file__))


    return os.path.abspath(
        os.path.join(this_dir, "..", "certifikat", "templates",
                     course_event.course_type.certificate_template))
