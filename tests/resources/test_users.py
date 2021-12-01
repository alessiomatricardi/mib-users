from .view_test import ViewTest
from faker import Faker
import json
import responses
from mib import create_app


class TestUsers(ViewTest):
    faker = Faker('it_IT')

    @classmethod
    def setUpClass(cls):
        super(TestUsers, cls).setUpClass()

    '''
    def test_delete_user(self):
        user = self.login_test_user()
        rv = self.client.delete('/user/%d' % user.id)
        assert rv.status_code == 202
    '''

    def test_01_register_and_get(self):
        # get a non-existent user
        data = {'requester_id': 1}
        rv = self.client.get('/users/0', json=data)
        assert rv.status_code == 404

        # registering a new user
        json_user = { 'email' : 'prova4@mail.com' , 'firstname': 'Barbara', 'lastname': 'Verdi', 
        'password' : 'prova123', 'date_of_birth': '1990-05-25'} 
        rv = self.client.post('/register', json = json_user)
        self.assertEqual(rv.status_code, 201)

        # registering again with the same email
        rv = self.client.post('/register', json = json_user)
        self.assertEqual(rv.status_code, 200)

        # retrieving the user by her email to check her id
        rv = self.client.get('/users/prova4@mail.com')

        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # get an existent user
        #user = self.login_test_user()
        data = {'requester_id' : test_id['id']}
        rv = self.client.get('/users/%s'% (str(test_id['id'])), json=data)
        assert rv.status_code == 200
        
    
    def test_02_get_user_by_email(self):

        # get a non-existent user with faked email
        data = {'requester_id': 1}
        rv = self.client.get('/users/%s' % TestUsers.faker.email(),
                             json=data)
        assert rv.status_code == 404
        # get an existent user
        user = self.login_test_user()
        rv = self.client.get('/users/%s' % user.email)
        assert rv.status_code == 200


    def test_03_modify_user_data(self):
        
        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/users/prova4@mail.com')
        
        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # personal data modification variables
        json_user_success = { 'requester_id' : test_id['id'] , 'firstname': 'Barbaro', 'lastname': 'Verde', 'date_of_birth': '1991-06-26'} 
        json_user_failure = { 'requester_id' : 200, 'firstname': 'Barbara', 'lastname': 'Verdi', 'date_of_birth': '1990-05-25'} 
        
        # try with wrong id and expect a 404 response
        rv = self.client.patch('/profile/data', json = json_user_failure)
        self.assertEqual(rv.status_code, 404)

        # try with correct id 
        rv = self.client.patch('/profile/data', json = json_user_success)
        self.assertEqual(rv.status_code, 200)

        # login with Barbara
        json_login = { 'email' : 'prova4@mail.com' , 'password': 'prova123'} 
        rv = self.client.post('/login', json = json_login)
        self.assertEqual(rv.status_code, 200)
  

        # password modification variables
        json_user_password_success= { 'requester_id' : test_id['id']  , 'old_password': 'prova123', 'new_password': 'abcd1234', 'repeat_new_password': 'abcd1234'} 
        json_user_password_wrong_id= { 'requester_id' : 200 , 'old_password': 'prova123', 'new_password': 'abcd1234', 'repeat_new_password': 'abcd1234'}
        json_user_password_wrong_old_pwd= { 'requester_id' : test_id['id']  , 'old_password': 'prova12345', 'new_password': 'abcd1234', 'repeat_new_password': 'abcd1234'}
        json_user_password_unchanged= { 'requester_id' : test_id['id']  , 'old_password': 'prova123', 'new_password': 'prova123', 'repeat_new_password': 'abcd1234'}
        json_user_password_not_corresponding= { 'requester_id' : test_id['id']  , 'old_password': 'prova123', 'new_password': 'abcd1234', 'repeat_new_password': 'wrongpwd'}
   
        # passing wrong id
        rv = self.client.patch('/profile/password', json = json_user_password_wrong_id)
        self.assertEqual(rv.status_code, 404)

        # passing wrong old password
        rv = self.client.patch('/profile/password', json = json_user_password_wrong_old_pwd)
        self.assertEqual(rv.status_code, 401)

        # passing the same password as the new one
        rv = self.client.patch('/profile/password', json = json_user_password_unchanged)
        self.assertEqual(rv.status_code, 400)

        # repeating wrongly the new password 
        rv = self.client.patch('/profile/password', json = json_user_password_not_corresponding)
        self.assertEqual(rv.status_code, 400)

        # passing everything as it should be
        rv = self.client.patch('/profile/password', json = json_user_password_success)
        self.assertEqual(rv.status_code, 200)

        # changing content filter test variables
        json_content_filter_enabling = {'requester_id': test_id['id'] , 'content_filter': True}
        json_content_filter_disabling = {'requester_id': test_id['id'] , 'content_filter': False}
        json_content_filter_wrong_id = {'requester_id': 200 , 'content_filter': True}

        # passing wrong id
        rv = self.client.patch('/profile/content_filter', json = json_content_filter_wrong_id)
        self.assertEqual(rv.status_code, 404)
        
        # enabling content filter
        rv = self.client.patch('/profile/content_filter', json = json_content_filter_enabling)
        self.assertEqual(rv.status_code, 200)

        # disabling content filter
        rv = self.client.patch('/profile/content_filter', json = json_content_filter_disabling)
        self.assertEqual(rv.status_code, 200)

    @responses.activate
    def test_04_pictures(self):

        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/users/prova4@mail.com')
        
        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # modify profile picture test variables
        json_pfp_wrong_id = {'id': 200, 'image': 'whatever'}
        img_base64 = '/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAoHCAwNCgoJDAgKCgoKCg8MCgoKCh8KDAkZJRQZGSUhJCQcIDAlHB4rLSQkNDgmKy8/NTU1GiQ7QEAzPy48UTEBDAwMEA8QERIQETEdGB0xNDQ0MTE/MTE0PzQxMTExMT8xMTExMTQ0NDExMTQxNDQ0MTE/MT8xMTExMTQ0NDE0Mf/AABEIAMgAyAMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAADAAECBAUGBwj/xABAEAACAQIEAwUGBAQEBQUAAAABAgMAEQQSITEFQVETImFxgQYykaGx8CNCwdFSouHxBxQzghUkQ2NyJTSSssL/xAAZAQEAAwEBAAAAAAAAAAAAAAAAAQIDBAX/xAAiEQEBAAICAgMAAwEAAAAAAAAAAQIRAzESIUFRYRMycQT/2gAMAwEAAhEDEQA/AOpdVYHYnlVCdGUcwKvggDxoDuDfNqKsoymHWpxva/SjTRjUrqKq2salC7G+/M1JrkHpVaN9vGrSkWoGjFr0UjShJoT50a1QlVlTmBsalFryozpe/wBKgihbsxCry6nyqLlJ3UzG1MrzoLoQfA0CfikSsUXvEaH81vP+lCTFTPb8NGB/huB9N/Os/wCX8X/j/VlU153pOjefyoU2NSFUZ0ILtlJI0S/X560aDiS3ysiunXJy+FLy/hOP9QJI60wLX8KvqsMwPZt2clvcbY0B8OymzAgj4Gr45TJS42Bqdqdl002qSpRlTS1W2hCFdqOFpIlvSpkb0AXNqHe7DnaiONOlVxcOOlBaAsB1qd6iraeFInegcmlSG3KlQFyetCmTQ8tKstpegSG96DOUMxPIXoTxNrbUVfygX61Gw2NNigqNcb71djXTwqLKPKiIflSoIp51K2VbmwA61LlVKeUu/Zr7o1JqmefjFscfKjmbN4KNj1rOx8/cOYtkH5FazP8Af/6o2IkCR72AFyT8fv8ArWXFh5cS5Zj2cZJYvbdfD7/auXyuV3XTMfGI4dJZpMsYjgjjfvOhsQR67/Kukw0SRxhTeQixzPdiT4b2oUGGWNFVUEaKO6LDQaW+NEF9SwKqRqeb9KvKjx2nKkMgAbsySe8LA2+NU2wSI2dbkaEAc/PXWroAcd2BwQNWJNv0oyYbMhBBUnXKdh5ffSnknwVYIu6vZvGoLaAWH6n41poFkTs3Qxv+XMAL+XWucdZIpCFjUAanOQAPv7FaGC4ta0cihwDtYdw87eVXllUyxsHlw7RuUbUflYbGki1qL2c0ZUkMh9xwNQfGs6WNo3Kty2PIitMct/6yyx0cD4U5qINSG1XVDZaCU18RVh6GpufWgdVsKRXUcqlb4U1EFalSG5pUBXa5IHKhHepOdfHnUQaJNloE5Fuh5VYPOqWIYkne1IBdpc0aN9apsCOtTje3lS+psn0s4ybKuVTZj8qrxLlQtud28TTE3OY3JY2UWp5D7qDQe8xudPrXDyZeV/HXhhqT7UcU13QtcqzZUQGzTkb+nU/0rbwGFKoC+jkBnFrKvhboBsPOsXgsJxGKkxLapGcsY/KgG331vXVGygJcEAd81GK9+gmUaMR3FPdB/wCofv61JIM5MjAAn3FtoBUox2jj+FdFUcq00jCjYWq09pk0Dh4so21GtWwgPIW53FRRfu9HVP7VfRazcbw+OQEFBe2lwK4jjGGnwsiZSxjNwrxkLkA9D99K9JZNDtfwrH4vgUxEUkbA6jRhuDyqL6VvtzPB+Lt3Vcm5N9QPgdenn9a6sqmIgEi2DpsP0NeVywvg8Y8bBgmYhTn0Py/rXdezfEe8qsSUfum51BO396ny9xnlitKvxFTFWcfDkkLKO7JrcbXqr1roxu457NVFxcUJFNz0vR6ZVtVkHtTWonKoEXoI2pVMJSoBNTDS+otTsu9QOg8qCBk1pnjzWqObvmjX2oKzw/SgugUADcm1XzsaoTN32tqF0tesubLWN/V+PHeSLHvAclA1HWo4kBYpZGvdI3Y5d9Faw+lNCczjkCbk9APsVPENmwkkhIHaMh73MGRbAem3i1cLsxWeEw9lCoNs17sPH709KsTynMIwQXc79f6ftQ0bLGH0sot60/DY2kcytrc924tpV5UzHdtbeAhCRrcd4i7E1c0qumwG9udEF/LpW2NRYJ8L1MN60C7eQqaDrTaNDZr+VAlXQ8+WlWAmgJvbrQ3003B0vS9IcF7ZcPYoMSqAhLiQAa2qhwSXuLyuO6b7f1vXZcYhV4ZY2AN0bQ9a4DhDlXxEYJPZSlRn3AOZdfLb4WrO1bT0qN/8xg0b8yre3j93rPqXAJ+48e4NmHre/wB+NExMeSRl2F7jyro4svWnLyYg0rUqVbMklPpUhah0qAmalQiN6egTjeguRVhhcVVdGB52BoK7Gz0YNcVCZLODsDUo126UQIxyozclW+tZUr6PzK6bVp4pgsTeNh9/OsaRu4ed2+FcvPfcjo4Z2ZJMqSHUEIVU36/Yq7OqlI4zaylGNjbbb52rMVhlF92kHw+7VceQsed2YDxIGWuV0xckGdI40sCx1Ph93rWwqoiBQyadDvauYSUNJIzSWSPuXvYG2/zvWbxHj2DQtGjtJIr5csbM7X8LA/CtcZ+J6nenoIxSra9mA5g6UZMWjC62NztXleA48zSKv4sV2IUyC6k+7yvsbj0rruEzO8gDaXtcA7ir718IkldFNimUmwNgAdqzcTx9IzbV3G4GgHrWm+FDRlrkG2XbeuM42jq4gwsQbESNbtHFkjH3zOlRdpmnSYbjM81iAkaHm+l6vZnsGEoYjUpbQ15PhH4w+I7FZZIzkzNJJH+Gh6Xtbb9q6TgvGOKLIMPi8E2S+VZ0SyH61azXyrLL8OulIkDKbqTdTm3BrgliMeMxUhBAzhJEsAUZf3FvgfCu4iLtGzPGVYNoCtq5riuG/wDU5EFgMZhDIt9BnX7H/wAjWeS8jW4W5QRyD3XjAPmNx8a1cYb5G3uLXrG4Yb4aPe6ORr1941ruc0QvqQwsatw5e45+bHtXtSpCleu1ylelfzpvnT3oGY09RPypUFpbeFRcLY7UmO9AcnWgq4wghbbg8qjCDpuPOiZLt1150UJloAY1fwz4EViYlrKOZsTa/wDtrdxY/Ck3uBeubxT7dNNL/wC6uP8A6O46eDpFWOcb+9YedWnbKkkmgMaXjvtfl+nxqgh1HUbef3ajYtyYo4xr20qA36e9+1c07dMnuBwcJmxEYV5ysUj99EXK8g87/OtfB+zGDjUL/kiykd4BS2c+N7+PxqzgmsFUAZVAHlXRwreNSRrbU2rfHf2nLFzU3AcIseWPBCNb3yKojUnlt60aCNUMYAC5bC171q4l7ZtrLqNt6zYGEkg5gPqfGl/0xnp0Ub5o1GwuKBicCjgExIxAtnsM1EjHcAFyQKg+MWMhHBAJsH5A+NWUsAhwUaHSCMWvbMlW44NDsAP4RanSdX/OOotzqzBItyDaxG9qnRf8UZyMhG5G+lcnx1wvEOE62LSSJfTYplt99K63EgB2tqDpXGe065cdwl8hNppB3Tt3c2vras8o0nTT4Ytkli1BD5kB6e8PlWkrXQbi63t41n4UsJCdgYym27D+lqtq1rgXADkDW9hUcfcYcs7OBTE70jz6UzGvQcRZhSDVArrpzp0U0Er0qe1KgKedCcb9aLzqD0EI11o7oLDY0JakTQVsUPw5OfcNcpi27yjkGNdhILgjqLVyPFIykpjOwe+1cv8A0Y+pW/BfdCjG3IhSak75pY9iqSqoA5c6aI6km47gPrVTte7HIeeMAPhXNi7J3HTQTBSLXsd9K2E4iUjIuLWuL8q5srlIN9OetAx2NZY+zW5d+6g8a1i91Wg+ObETNGrERr/qOvK9Dbi8eEkQZo2YNYoz2YmocLQRxhbgsTmc8yedaK4SGRgzhAdAXNr1OlbVzDe0qOrZEyyBLgBMx+VFws4xiFHglQBgzvJGY736dafCcLwkLCYSICdCzOLVo/5vCKLDF4cEf9xRUyK+/iMDEGbBTEMWMDm6OdLDxrUw2MDqCpBBF7jaqvGuI4J4XjfF4cgAlbSgm/hrWFwXElnHZOZIye6eR8qX0tj7nue3UyTFiBub1zntUpEnDZACSMQ62HUpXQIve1Fja/rXPe1E6ibhuH07SSdmA6AWX9apkNDDNeST/tyOvhrZqtJcoTuTYEnf+H7/APKs/ByKySOLgmUNbz+/5au4ZsyMN7Nfy91h+tV4v7Rjy9US1MRUrUrelei4UVFStpSpCgblT0mpUBCd6hapn0qNBHnSvT0xoG686wfaKLVJNdY8pt/u/St8Vn8YizwEgEsjZhptas+THyxq+F1lHNX7jdbHXy7tY/FsQ0ODQroxlOXW2ve/Y1sAaMOZXL6/d6w/aRFMcUZBIEjsFFvT51xYz27bfW3U4TELiMLFMuokjVhbW3UVLH4JHw/aJpIqNciuX9juIlUfBvcBGzR36c/n9a7LDtvGLFJBseVXvqr45bc5xLAYrDpHJFipzGcpdEk7MMPDTx/lrc4fwvASxrI+PnMhDDNJiTctkNufKxvWhPErRrGwDKFtYjlWFJwtkkLxFWUnWN2IIq+NTMZl86rr8F7O8ODx5sRNImQlkfEaE8rWt40TF4LhGHV/+WilcLbKy9o0ne8Tr8bmufwnbhFVYFUgm57U3Pz2rWwuBz3M2VSd8ikH1vVpYm8eu89z6ZKcITiGISeTCRRwQqUgijSypfe+g1+Q860uDYJcOphsB2bsu2n5q28NEqKAi5UXRFA5ULExhHZhoTvVMkeU6k1A3cAMduVcFxvEHEcbiykFMKAiE+7cXdvvqPj12Jmyq1rnIpawriuzZscZDoVuxUC9r73+fwrPLet/Cvzp0WANo+9pc3t0sv8AatLAX7KTnmkQ1kxMQir1W5HMd3+9bGCTLGAdCCGNuve/rVuHHdjHmvqj3p6VtTSrucZvrTDn1p6a/wAKBXpUiKeglmpr/Oo3pA0D3pEUqX7UDAUnUMpB1BFI86cCoo5biuFMUq5b5Ga9YHG4S0YIsSkjXJF9K7zimHSSB87qnZgssjnKEPjXJhVkDpdHWQd11OZfSuTkx8ct/FdXFl5TXzFDCYbCRQxyPJm4hJ/oxRvnKDuqc3zH0raw0zIVRrgDVCaysNgCkkZIUgPYsdCR+tdFNhQQARoVsKpct6bYzW/a9BOssY2zAWIpJAS4tYA9TYVjozwuDqQND4iteDFIwVrjS19dqmLxrwYBrAh1APQE1oYfBgAkkG3MC1ZScTVEF3GWw5Vcw/E0IvnFj1O1XmlbKvPlUEmwCi+tYmMxmdyF1totTx/EM90T82hYchVaGLKC51IG9VyJ6YvE24j2jnBiFo41C4lZGIck5dvTy3qlFGzEMyBGPv5fn/eujwUdgDIM0eKmfMD+Vvy/EC3oLb0XGcLzo5QLnCkxqTkUnkDVct2SIlktv25vH8RXCJGzIru7KI42bKD7t79NKqS+3YiEZOADrJ3tJcrAeOh8beFchxrHTtjJO3jKSQvk7F72S233z51lSTNIxZyWc/m6/etdHHj4yObky8rXoMv+IaqAf+Fkm5U/8zaxHdP5PLXxoKf4jXIzcLUA75cTr/8ASuAYbnnzNRA1+tbMtPVMF7d4GQhZo5sMSbZmUSIPgf0rpcNioZkEkM8csZ/NG4YeteEqat4DiE2FmSaCV45FI7yHQ+f7VO0XF7lSrC9m/aCPHxZWyx4uNQZIwbBx/EPDrSohtWqYqJGtOBQPalan+tUeK8YwmCj7TE4hYyRdIx3nk8h9jxoLhG/hvWFxv2owmBzRl+3xAGmHjYXQ+J5felcbx323xGIzRYW+EgNwWDfiuPEjb0+Nce8hJJ1JJ1JqEyOh4lx7G8TkjhMgRZpAkUEV1RL8zrr5/Su6wXBEw+FiijveNB3j/wBQ+Pma8t4XP2WIhxGxilRz5BtflevcoArxxyKQVdAysNQRvXPzXr6dHFJ7c3EmcFkue8yyIeo7vpreteAZ4UJ99BYgjWhphRHi5o9o8We0j091xlVvjofTxosMTJI3fJU8q55HRFeaJWBuNT4VmzwulyhNuY6VvzR3uRoTv41RmQjcaHn1qwwXxMrK0bEknnfaj4WRgQnaOQTYjYVeTCKXLEXB0v0o8WDCvyA60W8mhgowVDHpV11upUcxbyoWHXKoGh6VaRLkHXyqaz2FiIrYSRF0aNM8fgR3vrV2Jw0aSLqsiB19V0oc/dgk7ha65bA9Wo/D4cuFw62sVgQN55MtJPaHA/4kezweIcYhQZ4wFxaqPfX+L968wZbGvpTEYVZYpcO6Bo5Y2SRSNCDXz3xLBNh8TicG3vYeZ0PjZsv0tXRhfhhnPlRI050PL8KPao5d9q1ZoW9PKok60U7c6CfeFENDBYp4JI8RE7JJG2ZHXcW5eo+VNVcHu+RBpVJp7xSqtjMXFh4pMRNIscUYu7sfp93rzj2h9s58T2kOGvhsMbqWB/FkHj0Hl6k0RHQ+0/teuHEmEwbpJibFHmFpEw/5dOp+Q532rzfFTySyNLLI8kjtd3kcsx+NCLkk870rfOoTIgflTWolqRHzFBGEWcA2sdDevX/YHH/5jhq4d3BmwTCFxaxK/l+WnpXkQHhrXT+x3F/8jjosS5Iw0loMYOQB2b0Op9etZ547jTDLxr1rEYMSKLaOrZkYWBH3+1RSEsSGsZANSosGHUfPTcWsda1okUgFbFWAIINwRytTy4cW7RbBwc22g67cjpf4jax57i38mO8O4tY0CSHfMAR0rYeMOARYEWDDp99elVJoivhbcVGlpkz0wKkXUsL/AJb6fSonDlX/ADEedauFUHobnnVmXDArcCxtyFJDbPhi0GwFtfGrSJt0qUcRBsRerUcYzdAN71bRVLG+7HCvvSSBj4AbfzZa1ESwAGwGwqjh17XFNLYGOMd0m9x0ty6k/wCw1qqNfC9TjO2eXwhbQ9K8H9tUH/GuIWA70xY+ZX9xXvbjQ8rDW1eE+2WvFsS3NpCT4+//AErTH+0Vy6rlqa1K/lT9N63YotQTuego7DfnQG3HIVAKnunralSj5c6VShqe0HHp8fOzO7LAjnsYVayRjx8ep+g0rIt8txe96jenBqAvpyqQpjz6/WkRz+NSbTHrTgfLwplN7dalaoEbaj6ij4WUJIM2qOMsg2Fj+29CqJG/TyoPZv8AD7jnaRjhE8gM2HjDYR2P/uI/3Tbyt0ruUHr0tXz5wPiDK8SJL2WIgkD4SYboeYN+R2t8bg6e2+zfHEx+FLkCPFREJi4NjG3hrsdSPUcqyyxa45b9CYrCypIcThu/mH4uFdrJJ/4/wPv4Hn1qUE8GIDKvckj0kw7js5Iz5H5EaHka0SfjVPF8PgxGUyRgyJqkiHJJGfBhtWdjWVBMPlbTa/PSra7eNra1nLgcZGV7LiIljB1TGRCVgPBgQfU3qOPx0+HRc+DiZ5HCRGPFEgt6oLC2/lUdFu2iUBtVXFS3K4aLvySCzBDfIOd+g/sNag0zS4qXBJiBGsY7rLGO0ktlvYtcW1se5+a4NXsNhUhBCIAWOZmYlmc+J1v/AGqbL10iZSz1dmw2HEaBRYk6u1gM5qwD504AtyF/GkbUhtB27rE20UmvBvamTNxCZjvfN/K7ftXuHE5Ozwsr6jLGQPM14Jx6XPjMU1xoWAFufcT9/hV8O1cv61i33pVEnWpryrdgYiguKOwoT/ClCQ0qZOXWnoB3pwaVKgV9vGiDry56UqVBDNla3Xa9GBuPH60qVQER6+VN8fjSpVIS3UgjQg3BHKuo4Bx6WGWPEJIY8XEAl2/08Un8LD4WPI25609Kq3pL2DgPHIOIw9pG3ZzxgDEYdj+JEf1U6WO2vXbVI8qVKsL3W+PwQ5eFZ/HIc+GLBGZo2zFV/ODv8qVKovVWnccph/aVsT7QQYVsIMMsF4MMgvJJIuUm510Fr8t9ORrvcw05XpUqlWSTej5t96a/pSpUGH7T4jJhil7Zrlj0tXguLmMkkkje9I+ZtNiczfVv5aalVuPuo5P6xVYVJD9KVKt2CX7UNxSpUEEOvMWp6VKg/9k='
        json_pfp_updating_success = {'id': test_id['id'], 'image': img_base64}

        # updating profile picture with wrong user id
        rv = self.client.post('/profile/picture', json = json_pfp_wrong_id)
        self.assertEqual(rv.status_code, 404)

        # testing on the update of a profile picture with wrong image is not necessary since 
        # in the yml the format of the string encoding the image is already defined as base64

        # first successful update of the profile picture without already having one
        rv = self.client.post('/profile/picture', json = json_pfp_updating_success)
        self.assertEqual(rv.status_code, 200)
        
        # updating the profile picture image while already having one
        rv = self.client.post('/profile/picture', json = json_pfp_updating_success)
        self.assertEqual(rv.status_code, 200)

        # retrieving a profile picture with a wrong current user id
        rv = self.client.get('/users/200/picture/%s' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 404)

        # retrieving a profile picture with a wrong target user id
        rv = self.client.get('/users/%s/picture/200' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 404)

        # retrieving a profile picture with correct id
        rv = self.client.get('/users/%s/picture/%s' % (str(test_id['id']), str(test_id['id'])))
        self.assertEqual(rv.status_code, 200)

        # retrieving a user picture without having the blacklist microservice mocked
        rv = self.client.get('/users/%s/picture/1' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 500)

        # mocking
        app = create_app()

        BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
        REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

        responses.add(responses.GET, "%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(test_id['id'])),
                  json={ "blacklist": "[1]", 
                         "message": "Blacklist successfully retrieved", 
                        "status": "success"
                       }, 
                       status=200)

        # retrieving a non available user picture 
        rv = self.client.get('/users/%s/picture/1' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 401)

        # retrieving an available user picture 
        rv = self.client.get('/users/%s/picture/2' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 200)



    @responses.activate
    def test_05_get_recipients_list(self):
        # required mocking blacklist

        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/users/prova4@mail.com')
        
        assert rv.status_code == 200
        test_id = rv.get_json()['user']

        # retrieving recipients list for a non-existing user
        rv = self.client.get('/users', json = {'requester_id': 200})
        self.assertEqual(rv.status_code, 404)

        # retrieving recipients list without having the Blacklist microservice mocked
        rv = self.client.get('/users',  json = {'requester_id': test_id['id']})
        self.assertEqual(rv.status_code, 500)

        # mocking
        app = create_app()

        BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
        REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

        responses.add(responses.GET, "%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(test_id['id'])),
                  json={ "blacklist": "[]", 
                         "message": "Blacklist successfully retrieved", 
                        "status": "success"
                       }, 
                       status=200)

        rv = self.client.get('/users',  json = {'requester_id': test_id['id']})
        self.assertEqual(rv.status_code, 200)
        #print(rv.get_json())

    @responses.activate
    def test_06_get_arbitrary_user_info(self):
        # required mocking blacklist

        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/user_email/prova4@mail.com')
        test_id = rv.get_json()
        assert rv.status_code == 200

        # retrieving a non-existing target user from an existing one
        rv = self.client.get('/users/%s/list/200' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 404)

        # retrieving an existing target user from a non existing current user
        rv = self.client.get('/users/200/list/%s' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 404)

        # retrieving an existing target user from an existing current one without blacklist mocking
        rv = self.client.get('/users/%s/list/%s' % (str(test_id['id']),str(test_id['id'] - 1)))
        self.assertEqual(rv.status_code, 500)

        #target user test variables
        json_target_in_blacklist = { "blacklist": "[1]", "message": "Blacklist successfully retrieved", "status": "success"}
        
        # mocking
        app = create_app()

        BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
        REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

        # mocking the presence of the target user in current user's blacklist
        responses.add(responses.GET, "%s/blacklist/%s" % (BLACKLIST_ENDPOINT, str(test_id['id'])), json=json_target_in_blacklist, status=200)

        rv = self.client.get('/users/%s/list/1' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 401)

        # requesting a non blocked/blocking user
        rv = self.client.get('/users/%s/list/2' % (str(test_id['id'])))
        self.assertEqual(rv.status_code, 200)
        

    def test_07_unregister(self):

        # retrieve Barbara Verdi, our test dummy
        rv = self.client.get('/user_email/prova4@mail.com')
        test_id = rv.get_json()
        assert rv.status_code == 200

        # unregistration test variables
        json_user_unregistration_id_failure= { 'id' : 200  , 'password': 'abcd1234'} 
        json_user_unregistration_password_failure= { 'id' : test_id['id']  , 'password': 'notapassword'} 
        json_user_unregistration_success= { 'id' : test_id['id']  , 'password': 'abcd1234'} 

        # trying to unregister a non existing user
        rv = self.client.post('/unregister', json = json_user_unregistration_id_failure)
        self.assertEqual(rv.status_code, 404)

        # trying to unregister an existing user using the wrong password
        rv = self.client.post('/unregister', json = json_user_unregistration_password_failure)
        self.assertEqual(rv.status_code, 401)

        # unregistering an existing user using the correct password
        rv = self.client.post('/unregister', json = json_user_unregistration_success)
        self.assertEqual(rv.status_code, 200)
