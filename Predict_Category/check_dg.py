from pandas import isnull

def predict_dangerous(clean_product_name, wbn, category, dg_keywords, logger):
    keyword = "No keyword matched"
    contain_list = ""
    contain_cat = ""
    except_list = ""
    except_cat = ""
    dg_report = {}
    flag = None
    ## used to store whether the except_category or except_list has got a hit.
    exception_matched = False

    if isnull(category) or not category:
        category = 'Delhivery_Others'

    contain_failed = 0  
    except_failed = 0

    for row in dg_keywords:
        if row[1] in clean_product_name:
            temp = int(row[0])
            if temp == 1:
                flag = True
            else:
                flag = False
            keyword = row[1]
            if row[3]: #for matching the CONTAIN category
                wordList = row[3].split(", ")
                if except_failed == 2:
                    except_list = ""
                    except_cat = ""
                    except_failed = 0
                for x in wordList:
                    if x[1:-1] == category.lower():
                        flag = True
                        contain_cat = category.lower()
                        break
                if flag:
                    break
                contain_failed = 1
                contain_cat = "No Category Matched"
            if row[2]: #for matching CONTAIN keywords
                wordList = row[2].split(", ")
                if except_failed == 2:
                    except_list = ""
                    except_cat = ""
                    except_failed = 0
                for x in wordList:
                    #if any word matches, mark it dangerous
                    if x in clean_product_name:
                        flag = True
                        contain_list = x
                        break
                if flag:
                    break
                contain_failed = 1
                contain_list = "No Keyword Matched"
            if row[5]: #for matching the EXCEPT category
                exception_matched = False
                wordList = row[5].split(", ")
                if contain_failed == 1:
                    contain_list = ""
                    contain_cat = ""
                for x in wordList:
                    if x[1:-1] == category.lower():
                        except_list = x[1:-1]
                        #if any category matches, mark it non-dangerous
                        flag = False
                        exception_matched = True
                        break
                if not exception_matched:
                    except_failed = 1
                except_cat = "No Category Matched"

            if row[4]: #for matching EXCEPT_LIST keywords
                if contain_failed == 1:
                    contain_list = ""
                    contain_cat = ""
                if row[5] and not exception_matched:
                    wordList = row[4].split(", ")
                    for x in wordList:
                        if x in clean_product_name:
                            except_list = x
                            flag = False
                            break
                elif not row[5]:
                    wordList = row[4].split(", ")
                    for x in wordList:
                        if x in clean_product_name:
                            except_list = x
                            flag = False
                            break
                if flag:
                    except_list = "No Keyword Matched"
                    break

                except_failed = 2
            #if all other columns were empty, and only the KEYWORD matches, mark it dangerous
            if flag:
                break

    if keyword == "No keyword matched":
        flag = False

    dg_report["name"] = clean_product_name
    dg_report["wbn"] = wbn
    dg_report["dangerous"] = flag
    dg_report["keyword"] = keyword
    dg_report["contain_list"] = contain_list
    dg_report["contain_cat"]  = contain_cat
    dg_report["except_list"]  = except_list
    dg_report["except_cat"]   = except_cat
    
    logger.info('Check DG: Product Name: {} Report: {}'.format(
        clean_product_name, dg_report))

    return dg_report

