import threading
import requests
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def _send_via_sendgrid(subject, html_body, plain_body, recipient_email):
    api_key = getattr(settings, 'SENDGRID_API_KEY', '')
    from_email = settings.DEFAULT_FROM_EMAIL
    response = requests.post(
        'https://api.sendgrid.com/v3/mail/send',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'personalizations': [{'to': [{'email': recipient_email}]}],
            'from': {'email': from_email},
            'subject': subject,
            'content': [
                {'type': 'text/plain', 'value': plain_body},
                {'type': 'text/html', 'value': html_body},
            ],
        },
        timeout=30,
    )
    if response.status_code not in (200, 202):
        raise Exception(f'SendGrid API error {response.status_code}: {response.text}')


def _send(subject, template, context, recipient_email):
    """Internal helper — renders an HTML email and sends it in a background thread."""
    if not recipient_email:
        print(f'[EMAIL SKIPPED] "{subject}" — recipient has no email address set')
        return

    html_body = render_to_string(f'emails/{template}', context)
    plain_body = context.get('plain_message', subject)

    def _do_send():
        try:
            if getattr(settings, 'SENDGRID_API_KEY', ''):
                _send_via_sendgrid(subject, html_body, plain_body, recipient_email)
            else:
                send_mail(
                    subject=subject,
                    message=plain_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    html_message=html_body,
                    fail_silently=False,
                )
            logger.info('Email "%s" sent to %s', subject, recipient_email)
            print(f'[EMAIL OK] "{subject}" → {recipient_email}')
        except Exception as exc:
            logger.error('Failed to send email "%s" to %s: %s', subject, recipient_email, exc)
            print(f'[EMAIL ERROR] "{subject}" → {recipient_email} | Error: {exc}')

    threading.Thread(target=_do_send, daemon=True).start()


def send_application_under_review(application):
    email = application.submitted_by.email
    _send(
        subject=f'[Libya TradeNet] Application {application.application_number} — Under Review',
        template='application_under_review.html',
        context={'app': application},
        recipient_email=email,
    )


def send_application_approved(application):
    email = application.submitted_by.email
    _send(
        subject=f'[Libya TradeNet] Application {application.application_number} — Approved',
        template='application_approved.html',
        context={'app': application},
        recipient_email=email,
    )


def send_application_rejected(application):
    email = application.submitted_by.email
    _send(
        subject=f'[Libya TradeNet] Application {application.application_number} — Rejected',
        template='application_rejected.html',
        context={'app': application},
        recipient_email=email,
    )


def send_permit_under_review(permit):
    email = permit.created_by.email
    _send(
        subject=f'[Libya TradeNet] Permit {permit.permit_number} — Under Review',
        template='permit_under_review.html',
        context={'permit': permit},
        recipient_email=email,
    )


def send_permit_approved(permit):
    email = permit.created_by.email
    _send(
        subject=f'[Libya TradeNet] Permit {permit.permit_number} — Approved',
        template='permit_approved.html',
        context={'permit': permit},
        recipient_email=email,
    )


def send_otp(user, otp_code):
    _send(
        subject='[Libya TradeNet] Your Login Verification Code',
        template='otp_email.html',
        context={'user': user, 'otp_code': otp_code},
        recipient_email=user.email,
    )


def send_permit_rejected(permit):
    email = permit.created_by.email
    _send(
        subject=f'[Libya TradeNet] Permit {permit.permit_number} — Rejected',
        template='permit_rejected.html',
        context={'permit': permit},
        recipient_email=email,
    )
