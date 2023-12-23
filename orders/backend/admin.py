from django.contrib import admin

# from .models import Shop, Category, ShopCategory
#
#
# class ShopCategoryInline(admin.TabularInline):
#     model = ShopCategory
#     extra = 0
#
#
# @admin.register(Shop)
# class ShopAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'url']
#     list_filter = ['name']
#     inlines = [ShopCategoryInline]
#
#
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name']
#     list_filter = ['name']
#     inlines = [ShopCategoryInline]
