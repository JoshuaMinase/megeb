# Megeb — Ethiopian Recipe Platform

A people's recipe platform where anyone can share food and ingredients.
Features: dish feed with variation system, nationality-based recommendations, trending, search, auth, pantry, nutrition log, meal planner, AI recipe generation.

---

## Stack

- **Frontend** — plain HTML/CSS/JS (no build step)
- **Backend** — FastAPI + Motor (async MongoDB)
- **Database** — MongoDB (local or Atlas)

---


## How personalisation works

1. User signs up → chooses nationality
2. `GET /recipes/` checks JWT → gets user nationality
3. MongoDB aggregation scores matching-nationality recipes higher
4. `GET /api/dishes` returns approved dishes sorted by variation count + recency

## Moderation flow

1. User submits dish or variation → `status: "pending"`
2. Admin sees it in `/api/moderation/queue`
3. Admin approves → `status: "approved"`, appears in feed
4. Dish `variation_count` is incremented when a variation is approved

## Admin setup

Promote a user to admin directly in MongoDB:

```
db.users.updateOne({ email: "your@email.com" }, { $set: { role: "admin" } })
```
