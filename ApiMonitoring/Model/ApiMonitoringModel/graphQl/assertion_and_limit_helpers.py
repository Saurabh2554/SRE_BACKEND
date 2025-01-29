from ApiMonitoring.Model.ApiMonitoringModel.graphQl.helpers import get_service,get_metrices,get_assertions_for_service

def checkAssertion(serviceId,metriceId,response):

    service = get_service(serviceId=serviceId)
    metrices = get_metrices(metriceId=metriceId)
    assertionAndLimits = get_assertions_for_service(serviceId=serviceId)

    for assertion in assertionAndLimits:
        
        pass



    
    pass