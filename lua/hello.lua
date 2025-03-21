local _M = {}

function _M.greet(name)
    return ngx.say("Greeting from ", name)
end

return _M