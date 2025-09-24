from django.db import models

# stationery

class StationeryCategory(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name

class StationeryItem(models.Model):
    date = models.CharField(max_length=13)
    name = models.CharField(max_length=100, blank=False)
    category = models.ForeignKey(StationeryCategory, on_delete=models.SET_NULL, null=True)
    number_of_stationery = models.IntegerField(blank=False)
    per_price_stationery = models.IntegerField(blank=False)
    per_price_for_buy = models.IntegerField(blank=False)
    stationery_price = models.IntegerField(blank=False)
    stationery_paid_price = models.FloatField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TotalStationery(models.Model):
    stationery = models.ForeignKey(StationeryItem, on_delete=models.CASCADE)
    total_stationery = models.IntegerField()
    total_amount = models.IntegerField()
    per_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class BuyStationeryAgain(models.Model):
    stationery = models.ForeignKey(StationeryItem, on_delete=models.CASCADE)
    date = models.CharField(max_length=13)
    number_of_stationery = models.IntegerField(blank=False)
    per_price_stationery = models.IntegerField(blank=False)
    per_price_for_buy = models.IntegerField(blank=False)
    stationery_price = models.IntegerField(blank=False)
    stationery_paid_price = models.FloatField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.stationery.name

# book

class Books(models.Model):
    date = models.CharField(max_length=13)
    name = models.CharField(max_length=115, blank=False)
    number_of_book = models.IntegerField(blank=False)
    per_price = models.IntegerField(blank=False)
    per_book_price_for_buy = models.IntegerField(blank=False)
    price = models.IntegerField(blank=False)
    paid_price = models.IntegerField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class TotalBook(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    total_book = models.IntegerField()
    total_amount = models.IntegerField()
    per_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class BuyBookAgain(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    date = models.CharField(max_length=13)
    number_of_book = models.IntegerField(blank=False)
    per_price = models.IntegerField(blank=False)
    per_book_price_for_buy = models.IntegerField(blank=False)
    price = models.IntegerField(blank=False)
    paid_price = models.IntegerField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.book.name