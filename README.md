Mobile Swiss Army Knife Toolset
========================
This is a collection of tools for Apple's AppStore and Google Play.  The following is a brief description for every tools included.

AppReview
----------------------------------------
Code:      /appstore/appreview.py
Purpose: Download all the reviews for a given app in AppStore, including the published date, player, title, content, rating, reviewid, total reviews of publishers and total 5 star review count. Its main use include:
- Download all the review at one time to do customer service
- Check if a given app manipulate the reviews, because there should a lot of new users who only write 5 star reviews for that app.

Usage:  python3 appreview.py <appid>
Output: 
- review.csv: that will include all the reviews for the given app
- userreview.csv: that will include all the users' reviews for other app.
