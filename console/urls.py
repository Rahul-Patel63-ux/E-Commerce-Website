from django.urls import path
from .import views




urlpatterns = [

    path('dashboard/',views.consoleDashboard,name="console_dashboard"),
    path('',views.sign_in,name="sign-in"),
    path('sign-out/',views.sign_out,name="log-out"),
    path('signUp',views.signUp,name='signUp'),
    path('otpPage/<int:user_id>',views.otpPage,name='otpPage'),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),

    path('consoleGeneralSettings/',views.consoleGeneralSettings,name='consoleGeneralSettings'),

    #One time profile urls
    path('oneTimeProfile/',views.oneTimeProfile, name = 'oneTimeProfile'),

    #Profile urls
    path('showProfile/',views.showProfile,name= 'showProfile'),
    path('edit_profile/',views.edit_profile,name= 'edit_profile'),


    #Main category urls
    path('consoleMainCategory/', views.consoleMainCategory, name='consoleMainCategory'),
    path('consoleRenderData/',views.consoleRenderData, name='consoleRenderData'),
    path('categoryStatusChange/<int:pk>',views.categoryStatusChange, name='categoryStatusChange'),
    path('deleteCategory/<int:pk>',views.deleteCategory, name='deleteCategory'),
    path('updateCategory/<int:pk>',views.updateCategory, name='updateCategory'),

    #Sub category urls
    path('consoleSubCategory/',views.consoleSubCategory, name='consoleSubCategory'),
    path('subCategoryRenderData/',views.subCategoryRenderData, name= 'subCategoryRenderData'),
    path('subCategoryStatusChange/<int:pk>', views.subCategoryStatusChange, name='subCategoryStatusChange'),
    path('deleteSubCategory/<int:pk>',views.deleteSubCategory, name='deleteSubCategory'),
    path('updateSubCategory/<int:pk>', views.updateSubCategory, name='updateSubCategory'),


    #Nationality urls

    path('nationality/',views.nationality,name='nationality'),
    path('nationalityRenderData/',views.nationalityRenderData, name='nationalityRenderData'),
    path('nationalityStatusChange/<int:pk>',views.nationalityStatusChange, name='nationalityStatusChange'),
    path('deleteNationality/<int:pk>', views.deleteNationality, name='deleteNationality'),
    path('updateNationality/<int:pk>',views.updateNationality, name='updateNationality'),


    #urls for Gender
    path('gender-data-list/', views.gender_data_list, name='gender-data-list'),
    path('gender-data-table/', views.gender_data_table, name='gender_data_table'),
    path('update-gender/<int:pk>', views.update_gender, name='update-gender'),
    path('gender-toggle/<int:pk>', views.gender_status_change, name='gender-status-change'),
    path('gender-delete/', views.delete_gender, name='delete-gender'),

    #Contact us urls
    path('generalSettingsContactUs/',views.generalSettingsContactUs, name='generalSettingsContactUs'),
    path('contactUsDataRender/',views.contactUsDataRender, name='contactUsDataRender'),
    path('contactUsStatusChange/<int:pk>',views.contactUsStatusChange, name='contactUsStatusChange'),
    path('deleteContactUs/<int:pk>',views.deleteContactUs, name='deleteContactUs'),
    path('updateContactUs/<int:pk>',views.updateContactUs, name='updateContactUs'),


    #Salutation urls
    path('generalSettingsSalutation', views.generalSettingsSalutation, name='generalSettingsSalutation'),
    path('salutationRenderData',views.salutationRenderData, name='salutationRenderData'),
    path('salutationStatusChange/<int:pk>',views.salutationStatusChange, name='salutationStatusChange'),
    path('deleteSalutation/<int:pk>',views.deleteSalutation, name='deleteSalutation'),
    path('updateSalutation/<int:pk>',views.updateSalutation, name='updateSalutation'),

    #Brand urls
    path('generalSettingsBrand/',views.generalSettingsBrand, name='generalSettingsBrand'),
    path('brandRenderData/',views.brandRenderData, name='brandRenderData'),
    path('brandStatusChange/<int:pk>',views.brandStatusChange, name='brandStatusChange'),
    path('deleteBrand/<int:pk>',views.deleteBrand, name='deleteBrand'),
    path('updateBrand/<int:pk>',views.updateBrand, name='updateBrand'),

    #Product Material urls
    path('generalSettingsProductMaterial/', views.generalSettingsProductMaterial, name='generalSettingsProductMaterial'),
    path('materialRenderData/', views.materialRenderData, name='materialRenderData'),
    path('materialStatusChange/<int:pk>', views.materialStatusChange, name='materialStatusChange'),
    path('deleteMaterial/<int:pk>', views.deleteMaterial, name='deleteMaterial'),
    path('updateMaterial/<int:pk>', views.updateMaterial, name='updateMaterial'),

    #Product size urls
    path('generalSettingProductSize/',views.generalSettingProductSize, name='generalSettingProductSize'),
    path('sizeRenderData/',views.sizeRenderData, name='sizeRenderData'),
    path('sizeStatusChange<int:pk>/',views.sizeStatusChange, name='sizeStatusChange'),
    path('deleteSize<int:pk>/',views.deleteSize, name='deleteSize'),
    path('updateSize<int:pk>/',views.updateSize, name='updateSize'),

    #Product tag urls
    path('generalSettingsProductTag/',views.generalSettingsProductTag, name='generalSettingsProductTag'),
    path('tagRenderData/',views.tagRenderData, name='tagRenderData'),
    path('tagStatusChange/<int:pk>',views.tagStatusChange, name='tagStatusChange'),
    path('deleteTag/<int:pk>',views.deleteTag, name='deleteTag'),
    path('updateTag/<int:pk>',views.updateTag, name='updateTag'),

    #Product payment type urls
    path('generalSettingProductPaymentType', views.generalSettingProductPaymentType, name='generalSettingProductPaymentType'),
    path('paymentTypeRenderData', views.paymentTypeRenderData, name='paymentTypeRenderData'),
    path('paymentTypeStatusChange/<int:pk>', views.paymentTypeStatusChange, name='paymentTypeStatusChange'),
    path('deletePaymentType/<int:pk>', views.deletePaymentType, name='deletePaymentType'),
    path('updatePaymentType/<int:pk>', views.updatePaymentType, name='updatePaymentType'),

    #Product color urls
    path('generalSettingProductColor/', views.generalSettingProductColor, name= 'generalSettingProductColor'),
    path('colorRenderData/', views.colorRenderData, name= 'colorRenderData'),
    path('colorStatusChange/<int:pk>', views.colorStatusChange, name= 'colorStatusChange'),
    path('deleteColor/<int:pk>', views.deleteColor, name= 'deleteColor'),
    path('updateColor/<int:pk>', views.updateColor, name= 'updateColor'),

    #Product management

    path('consoleProduct/',views.consoleProduct, name = 'consoleProduct'),
    path('consoleProductCreate/',views.consoleProductCreate, name = 'consoleProductCreate'),


    #vendor type urls
    path('vendorType/',views.vendorType, name ='vendorType'),
    path('vendorTypeRenderData/',views.vendorTypeRenderData, name ='vendorTypeRenderData'),
    path('vendorStatusChange/<int:pk>',views.vendorStatusChange, name ='vendorStatusChange'),
    path('deleteVendorType/<int:pk>',views.deleteVendorType, name ='deleteVendorType'),
    path('updateVendorType/<int:pk>',views.updateVendorType, name ='updateVendorType'),

#finance and accounts starts here|

    #vendor Account type urls
    path('accountType/',views.accountType, name = 'accountType'),
    path('accountTypeRenderData/',views.accountTypeRenderData, name = 'accountTypeRenderData'),
    path('accountStatusChange/<int:pk>',views.accountStatusChange, name = 'accountStatusChange'),
    path('accountTypeDelete/<int:pk>',views.accountTypeDelete, name = 'accountTypeDelete'),
    path('accountTypeUpdate/<int:pk>',views.accountTypeUpdate, name = 'accountTypeUpdate'),


    #vendor bank names urls
    path('bankName/',views.bankName, name='bankName'),
    path('bankNameRenderData/',views.bankNameRenderData, name='bankNameRenderData'),
    path('bankStatusChange/<int:pk>',views.bankStatusChange, name='bankStatusChange'),
    path('bankDelete/<int:pk>',views.bankDelete, name='bankDelete'),
    path('bankUpdate/<int:pk>',views.bankUpdate, name='bankUpdate'),

    #upi urls starts here
    path('vendorUpi/', views.vendorUpi, name='vendorUpi'),
    path('upiRenderData/', views.upiRenderData, name='upiRenderData'),
    path('upiStatusChange/<int:pk>/', views.upiStatusChange, name='upiStatusChange'),
    path('deleteUpi/<int:pk>/', views.deleteUpi, name='deleteUpi'),
    path('updateUpi/<int:pk>/', views.updateUpi, name='updateUpi'),


    #account details starts here
    path('accountDetail/',views.accountDetail,name='accountDetail'),
    path('accountDetailRenderData/',views.accountDetailRenderData,name='accountDetailRenderData'),
    path('accountDetailStatusChange/<int:pk>',views.accountDetailStatusChange,name='accountDetailStatusChange'),
    path('deleteAccountDetail/<int:pk>',views.deleteAccountDetail,name='deleteAccountDetail'),
    path('updateAccountDetail/<int:pk>',views.updateAccountDetail,name='updateAccountDetail'),

    #Vendor management urls
    path('vendorManagement/',views.vendorManagement, name='vendorManagement'),
    path('vendorDataRender/',views.vendorDataRender, name='vendorDataRender'),
    path('deleteVendor/<int:pk>',views.deleteVendor, name='deleteVendor'),
    path('updateVender/<int:pk>',views.updateVender, name='updateVender'),
    path('vendorStatusChange/<int:pk>',views.vendorStatusChange, name='vendorStatusChange'),


    #Locations urls starts here
    #country urls
    path('vendorCountry/',views.vendorCountry, name= 'vendorCountry'),
    path('countryRenderData/',views.countryRenderData, name= 'countryRenderData'),
    path('countryStatusChange/<int:pk>',views.countryStatusChange, name= 'countryStatusChange'),
    path('deleteCountry/<int:pk>',views.deleteCountry, name= 'deleteCountry'),
    path('updateCountry/<int:pk>',views.updateCountry, name= 'updateCountry'),

    #state urls
    path('vendorState/', views.vendorState, name='vendorState'),
    path('stateRenderData/', views.stateRenderData, name='stateRenderData'),
    path('stateStatusChange/<int:pk>', views.stateStatusChange, name='stateStatusChange'),
    path('deleteState/<int:pk>', views.deleteState, name='deleteState'),
    path('updateState/<int:pk>', views.updateState, name='updateState'),

    # City URLs
    path('vendorCity/', views.vendorCity, name='vendorCity'),
    path('cityRenderData/', views.cityRenderData, name='cityRenderData'),
    path('cityStatusChange/<int:pk>', views.cityStatusChange, name='cityStatusChange'),
    path('deleteCity/<int:pk>', views.deleteCity, name='deleteCity'),
    path('updateCity/<int:pk>', views.updateCity, name='updateCity'),
    path('get_states_by_country/', views.get_states_by_country, name='getStatesByCountry'),

    #Area urls
    path('vendorArea/',views.vendorArea, name= 'vendorArea'),

    path('areaRenderData', views.areaRenderData, name='areaRenderData'),
    path('areaStatusChange/<int:pk>/', views.areaStatusChange, name='areaStatusChange'),
    path('deleteArea/<int:pk>/', views.deleteArea, name='deleteArea'),
    path('updateArea/<int:pk>/', views.updateArea, name='updateArea'),
    path('get_cities_by_state', views.get_cities_by_state, name='getCitiesByState'),
    path('get_states_by_country', views.get_states_by_country, name='getStatesByCountry'),


    # ajax urls
    path('get_states/', views.get_states, name='get_states'),
    path('get_cities/', views.get_cities, name='get_cities'),
    path('get_areas/', views.get_areas, name='get_areas'),
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),


    #product catalogue urls
    path('productCatalogue/',views.productCatalogue, name= 'productCatalogue'),
    path('productcatalogueRenderData/',views.productcatalogueRenderData, name= 'productcatalogueRenderData'),
    path('productcatalogueStatusChange/<int:pk>',views.productcatalogueStatusChange, name= 'productcatalogueStatusChange'),
    path('deleteProductCatalogue/<int:pk>',views.deleteProductCatalogue, name= 'deleteProductCatalogue'),
    path('updateProductCatalogue/<int:pk>',views.updateProductCatalogue, name= 'updateProductCatalogue'),
    path('showProductCatalogue/<int:pk>',views.showProductCatalogue, name = 'showProductCatalogue'),

    #Product Purchase management urls
    path('viewAllPurchasesTable/',views.viewAllPurchasesTable, name = 'viewAllPurchasesTable'),
    #create purchase url
    path('purchaseManagement/',views.purchaseManagement, name = 'purchaseManagement'),
    path('purchaseRenderData/',views.purchaseRenderData, name = 'purchaseRenderData'),
    path('purchaseItemStatusChange/<int:item_id>',views.purchaseItemStatusChange, name = 'purchaseItemStatusChange'),
    path('deletePurchase/<int:invoice_id>',views.deletePurchase, name = 'deletePurchase'),
    path('editPurchase/<int:invoice_id>',views.editPurchase, name = 'editPurchase'),
    path('viewPurchaseInvoice/<int:invoice_id>/', views.view_purchase_invoice, name='viewPurchaseInvoice'),

    path('get_mrp/<int:product_id>/',views.get_mrp, name = 'get_mrp'),
    path('get_vendor_details/', views.get_vendor_details, name='get_vendor_details'),

    #convert invoice to pdf
    path('invoice/<str:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),


    #stock management urls
    path('stockManagementListProducts/',views.stockManagementListProducts, name='stockManagementListProducts'),
    path('stockManagementRenderData/',views.stockManagementRenderData, name='stockManagementRenderData'),
    #inventory
    path('stockManagementInventory/<int:pk>',views.stockManagementInventory, name='stockManagementInventory'),


    #Order management urls
    path('consoleOrderManagement/', views.consoleOrderManagement, name = 'consoleOrderManagement'),
    path('myOrdersView/', views.myOrdersView, name = 'myOrdersView'),
    path('myOrderViewRenderData/', views.myOrderViewRenderData, name = 'myOrderViewRenderData'),
    path('update_order_status/<int:order_id>', views.update_order_status, name = 'update_order_status'),

    #pending orders urls
    path('pendingOrdersView/',views.pendingOrdersView, name='pendingOrdersView'),
    path('pendingOrdersRenderData/',views.pendingOrdersRenderData, name='pendingOrdersRenderData'),

    #cancel orders urls
    path('cancelOrdersView/',views.cancelOrdersView, name='cancelOrdersView'),
    path('cancelOrdersRenderData/',views.cancelOrdersRenderData, name='cancelOrdersRenderData'),

    #view order details
    path('view_order_details/<int:order_id>', views.view_order_details, name='viewOrderDetails'),

    # Transport type urls
    path('transportType' , views.transportType, name='transportType'),
    path('transportTypeRenderData' , views.transportTypeRenderData, name='transportTypeRenderData'),
    path('transportTypeStatusChange/<int:pk>/' , views.transportTypeStatusChange, name='transportTypeStatusChange'),
    path('deleteTransportType/<int:pk>/' , views.deleteTransportType, name='deleteTransportType'),
    path('updateTransportType/<int:pk>/' , views.updateTransportType, name='updateTransportType'),

    #packing urls
    path('packingManagementView/',views.packingManagementView, name='packingManagementView'),
    path('packingManagementStatusChange/<int:packing_status_id>/',views.packingManagementStatusChange, name='packingManagementStatusChange'),

    #  Orders packed urls
    path('packingManagementPackedView/',views.packingManagementPackedView, name='packingManagementPackedView'),
    path('packingManagementPackedRenderData/',views.packingManagementPackedRenderData, name='packingManagementPackedRenderData'),


    # Orders yet to pack urls
    path('packingManagementYetToPackView/',views.packingManagementYetToPackView, name='packingManagementYetToPackView'),
    path('packingManagementYettopackRenderData/',views.packingManagementYettopackRenderData, name='packingManagementYettopackRenderData'),

    path('packingOrderDetails/<int:order_id>/', views.packingOrderDetails, name='packingOrderDetails'),
    path('packingOrderDetailsPDF/<int:order_id>/', views.packingOrderDetailsPDF, name='packingOrderDetailsPDF'),

    # Transport details URL
    path('transportDetailsForm/<int:order_id>/', views.transportDetailsForm, name='transportDetailsForm'),
    path('viewTransportDetails/<int:order_id>/', views.viewTransportDetails, name='viewTransportDetails'),

    # accepted orders urls in finance and accounts

    path('acceptedOrderViewRenderData/',views.acceptedOrderViewRenderData,name='acceptedOrderViewRenderData'),


    #finance and accounts urls
    path('financeAndAccountsShow/',views.financeAndAccountsShow,name='financeAndAccountsShow'),

    # profit and lose
    path('profitAndLose/',views.profitAndLose, name='profitAndLose'),
    path('reports/',views.reports, name='reports'),
    path('expenses/',views.expenses, name='expenses'),
    path('refund/',views.refund, name='refund'),

    #banner urls
    path('banner/', views.banner, name='banner'),
    path('bannerRenderData/', views.bannerRenderData, name='bannerRenderData'),
    path('bannerStatusChange/<int:pk>', views.bannerStatusChange, name='bannerStatusChange'),
    path('deleteBanner/<int:pk>', views.deleteBanner, name='deleteBanner'),
    path('updateBanner/<int:pk>', views.updateBanner, name='updateBanner'),

    # Services urls
    path('services/', views.services, name='services'),
    path('servicesRenderData/', views.servicesRenderData, name='servicesRenderData'),
    path('servicesStatusChange/<int:pk>', views.servicesStatusChange, name='servicesStatusChange'),
    path('deleteServices/<int:pk>', views.deleteServices, name='deleteServices'),
    path('updateServices/<int:pk>', views.updateServices, name='updateServices'),




]
