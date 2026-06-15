"""Shopify Admin API — order/customer lookup backbone used by ALL channels.

Not an inbound message channel itself (email/social bring the message); this provides the order data
the reply is personalised with. Read-only here. Refunds are a gated money action handled separately.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

API_VERSION = "2024-10"


class Shopify:
    def __init__(self) -> None:
        self.store = os.environ.get("SHOPIFY_STORE", "fan-decor-1.myshopify.com")
        self.token = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
        self.base = f"https://{self.store}/admin/api/{API_VERSION}/graphql.json"

    def _query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(
            self.base,
            headers={"X-Shopify-Access-Token": self.token, "Content-Type": "application/json"},
            json={"query": query, "variables": variables},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()

    def lookup_order(self, order_hint: str, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find an order by name (#1234) or customer email; return normalised order detail."""
        if order_hint:
            search = f"name:{order_hint.lstrip('#')}"
        elif email:
            search = f"email:{email}"
        else:
            return None
        q = """
        query($q: String!) {
          orders(first: 1, query: $q, sortKey: CREATED_AT, reverse: true) {
            edges { node {
              name email createdAt displayFulfillmentStatus displayFinancialStatus
              totalPriceSet { shopMoney { amount currencyCode } }
              totalRefundedSet { shopMoney { amount } }
              customer { firstName lastName }
              lineItems(first: 10) { edges { node { title quantity sku } } }
              fulfillments(first: 5) {
                trackingInfo { company number url }
                displayStatus
              }
            } }
          }
        }"""
        data = self._query(q, {"q": search})
        edges = data.get("data", {}).get("orders", {}).get("edges", [])
        if not edges:
            return None
        return self._normalise(edges[0]["node"])

    @staticmethod
    def _normalise(node: Dict[str, Any]) -> Dict[str, Any]:
        cust = node.get("customer") or {}
        fulfil = (node.get("fulfillments") or [{}])
        tracking = {}
        if fulfil and fulfil[0].get("trackingInfo"):
            tracking = (fulfil[0]["trackingInfo"] or [{}])[0]
        money = node.get("totalPriceSet", {}).get("shopMoney", {})
        refunded = (node.get("totalRefundedSet") or {}).get("shopMoney", {})
        return {
            "order_number": node.get("name"),
            "email": node.get("email"),
            "customer_first_name": cust.get("firstName"),
            "created_at": node.get("createdAt"),
            "financial_status": node.get("displayFinancialStatus"),
            "fulfillment_status": node.get("displayFulfillmentStatus"),
            "total": money.get("amount"),
            "total_refunded": refunded.get("amount") or "0.00",
            "currency": money.get("currencyCode"),
            "line_items": [e["node"] for e in node.get("lineItems", {}).get("edges", [])],
            "tracking_company": tracking.get("company"),
            "tracking_number": tracking.get("number"),
            "tracking_url": tracking.get("url"),
        }
