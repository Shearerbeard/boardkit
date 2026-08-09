---
source: https://docs.stripe.com/webhooks
date: 2026-08-09
artifact: doc-excerpt
license: Proprietary (Stripe, Inc.) - short quoted excerpt for internal eval only
note: Page opening through the Create a handler requirements list; user-named canonical clean technical writing. Fetched verbatim from Stripe's own markdown export (docs.stripe.com/webhooks.md).
---

# Receive Stripe events in your webhook endpoint

Listen for events from Stripe on your webhook endpoint so your integration can automatically trigger reactions.

> #### Send events to your AWS account or Azure subscription
> 
> You can send events directly to [Amazon EventBridge](https://docs.stripe.com/event-destinations/eventbridge.md) or [Azure Event Grid](https://docs.stripe.com/event-destinations/eventgrid.md) as event destinations.

Create an event destination to receive events at an HTTPS webhook endpoint. After you register a webhook endpoint, Stripe can push real-time event data to your application’s webhook endpoint when [events](https://docs.stripe.com/event-destinations.md#events-overview) happen in your Stripe account. Stripe uses HTTPS to send webhook events to your app as a JSON payload that includes an [Event object](https://docs.stripe.com/api/events.md).

Receiving webhook events helps you respond to asynchronous events, such as when a customer’s bank confirms a payment, a customer disputes a charge, or a recurring payment succeeds.

## Get started 

To start receiving webhook events in your app:

1. Create a webhook endpoint handler to receive event data POST requests.
2. Test your webhook endpoint handler locally using the Stripe CLI.
3. Create a new [event destination](https://docs.stripe.com/event-destinations.md) for your webhook endpoint.
4. Secure your webhook endpoint.

You can register and create one endpoint to handle several different event types at the same time, or set up individual endpoints for specific events.

## Unsupported event type behaviors for organization event destinations

Stripe sends most event types asynchronously, but waits for a response for some event types. In these cases, Stripe behaves differently based on whether or not the event destination responds.

If your event destination receives [Organization](https://docs.stripe.com/get-started/account/orgs.md) events, those requiring a response have the following limitations:

- You can’t subscribe to `issuing_authorization.request` for organization destinations. Instead, set up a [webhook endpoint](https://docs.stripe.com/webhooks.md#example-endpoint) in a Stripe account within the organization to subscribe to this event type. Use `issuing_authorization.request` to authorize purchase requests in real-time.
- Organization destinations receiving `checkout_sessions.completed` can’t [handle redirect behavior](https://docs.stripe.com/checkout/fulfillment.md#redirect-hosted-checkout) when you embed [Checkout](https://docs.stripe.com/payments/checkout.md) directly in your website or redirect customers to a Stripe-hosted payment page. To influence Checkout redirect behavior, process this event type with a [webhook endpoint](https://docs.stripe.com/webhooks.md#example-endpoint) configured in a Stripe account within the organization.
- Organization destinations responding unsuccessfully to an `invoice.created` event can’t influence [automatic invoice finalization when using automatic collection](https://docs.stripe.com/billing/subscriptions/webhooks.md#understand). You must process this event type with a [webhook endpoint](https://docs.stripe.com/webhooks.md#example-endpoint) configured in a Stripe account within the organization to trigger automatic invoice finalization.

## Create a handler

Set up an HTTP or HTTPS endpoint function that can accept webhook requests with a POST method. If you’re still developing your endpoint function on your local machine, it can use HTTP. After it’s publicly accessible, your webhook endpoint function must use HTTPS.

Set up your endpoint function so that it:

- Handles POST requests with a JSON payload consisting of an [event object](https://docs.stripe.com/api/events/object.md).
- For [organization](https://docs.stripe.com/get-started/account/orgs.md) event handlers, it inspects the `context` value to determine which account in an organization generated the event, then sets the `Stripe-Context` header corresponding to the `context` value.
- Quickly returns a successful status code (`2xx`) prior to any complex logic that might cause a timeout. For example, you must return a `200` response before updating a customer’s invoice as paid in your accounting system.
